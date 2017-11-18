 # -*- Mode:Pythoon; c-file-style:"gnu"; indent-tabs-mode:nil; -*- */
 #
 # Copyright (c) 2016 NITK Surathkal
 #
 # This program is free software; you can redistribute it and/or modify
 # it under the terms of the GNU General Public License version 2 as
 # published by the Free Software Foundation;
 #
 # This program is distributed in the hope that it will be useful,
 # but WITHOUT ANY WARRANTY; without even the implied warranty of
 # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 # GNU General Public License for more details.
 #
 # You should have received a copy of the GNU General Public License
 # along with this program; if not, write to the Free Software
 # Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 #
 # Authors: Shravya Ks <shravya.ks0@gmail.com>
 #          Smriti Murali <m.smriti.95@gmail.com>
 #          Mohit P. Tahiliani <tahiliani@nitk.edu.in>
 #
 
 # Network topology
 #
 #    10Mb/s, 2ms                            10Mb/s, 4ms
 # n0--------------|                    |---------------n4
 #                 |    1.5Mbps, 20ms   |
 #                 n2------------------n3
 #    10Mb/s, 3ms  |  QueueLimit = 100  |    10Mb/s, 5ms
 # n1--------------|                    |---------------n5






import ns.core
import ns.point_to_point
import ns.internet
import ns.applications
import ns.network
import ns.flow_monitor
import ns.traffic_control
import sys
  
  
def main(argv):
    ns.core.LogComponentEnable("PieQueueDisc",ns.core.LOG_LEVEL_INFO)
    pieLinkDataRate = "1.5Mbps"
    pieLinkDelay = "20ms"
    
        
    n0n2 = ns.network.NodeContainer()
    n1n2 = ns.network.NodeContainer()
    n2n3 = ns.network.NodeContainer()
    n3n4 = ns.network.NodeContainer()
    n3n5 = ns.network.NodeContainer()
    
    i0i2 = ns.internet.Ipv4InterfaceContainer()
    i1i2 = ns.internet.Ipv4InterfaceContainer()
    i2i3 = ns.internet.Ipv4InterfaceContainer()
    i3i4 = ns.internet.Ipv4InterfaceContainer()
    i3i5 = ns.internet.Ipv4InterfaceContainer()
  
    writeForPlot = 0
    writePcap = 0
    flowMonitor = 0
    
    printPieStats = 1

    global_start_time = 0.0
    sink_start_time = global_start_time
    client_start_time = global_start_time + 1.5
    global_stop_time = 7.0
    sink_stop_time = global_stop_time + 3.0
    client_stop_time = global_stop_time - 2.0

    
    checkTimes = 0
    
    # Configuration and command line parameter parsing
    # Will only save in the directory if enable opts below
    pathOut = "." # Current directory
    
    
    cmd = ns.core.CommandLine()
    cmd.isMinstrelPie=0
    cmd.AddValue ("pathOut", "Path to save results from --writeForPlot/--writePcap/--writeFlowMonitor")
    cmd.AddValue ("writeForPlot", "<0/1> to write results for plot (gnuplot)")
    cmd.AddValue ("writePcap", "<0/1> to write results in pcapfile")
    cmd.AddValue ("writeFlowMonitor", "<0/1> to enable Flow Monitor and write their results")
    cmd.AddValue ("isMinstrelPie", "<0/1> to enable/disable Minstrel PIE", )

    cmd.Parse (sys.argv)
    
    isMinstrelPie = int(cmd.isMinstrelPie)
    
    
    
    print "Create nodes"
   
    c = ns.network.NodeContainer()
    c.Create(6)
    ns.core.Names.Add ("N0", c.Get(0))
    ns.core.Names.Add ("N1", c.Get(1))
    ns.core.Names.Add ("N2", c.Get(2))
    ns.core.Names.Add ("N3", c.Get(3))
    ns.core.Names.Add ("N4", c.Get(4))
    ns.core.Names.Add ("N5", c.Get(5))
    
    
    n0n2 = ns.network.NodeContainer ( ns.network.NodeContainer(c.Get(0)), ns.network.NodeContainer(c.Get(2)) )
    n1n2 = ns.network.NodeContainer ( ns.network.NodeContainer(c.Get(1)), ns.network.NodeContainer(c.Get(2)) )
    n2n3 = ns.network.NodeContainer ( ns.network.NodeContainer(c.Get(2)), ns.network.NodeContainer(c.Get(3)) )
    n3n4 = ns.network.NodeContainer ( ns.network.NodeContainer(c.Get(3)), ns.network.NodeContainer(c.Get(4)) )
    n3n5 = ns.network.NodeContainer ( ns.network.NodeContainer(c.Get(3)), ns.network.NodeContainer(c.Get(5)) )
    
    ns.core.Config.SetDefault ("ns3::TcpL4Protocol::SocketType", ns.core.StringValue ("ns3::TcpNewReno"))
    # 42 = headers size
    ns.core.Config.SetDefault ("ns3::TcpSocket::SegmentSize", ns.core.UintegerValue (1000 - 42))
    ns.core.Config.SetDefault ("ns3::TcpSocket::DelAckCount", ns.core.UintegerValue (1))
    ns.core.GlobalValue.Bind ("ChecksumEnabled", ns.core.BooleanValue (0))

    meanPktSize = 1000
    
    # PIE params
    print "Set PIE params"
    
    ns.core.Config.SetDefault ("ns3::PieQueueDisc::Mode", ns.core.StringValue ("QUEUE_DISC_MODE_PACKETS"))
    ns.core.Config.SetDefault ("ns3::PieQueueDisc::MeanPktSize", ns.core.UintegerValue (meanPktSize))
    ns.core.Config.SetDefault ("ns3::PieQueueDisc::DequeueThreshold", ns.core.UintegerValue (10000))
    ns.core.Config.SetDefault ("ns3::PieQueueDisc::QueueDelayReference", ns.core.TimeValue (ns.core.Seconds (0.02)))
    ns.core.Config.SetDefault ("ns3::PieQueueDisc::MaxBurstAllowance", ns.core.TimeValue (ns.core.Seconds (0.1)))
    ns.core.Config.SetDefault ("ns3::PieQueueDisc::QueueLimit", ns.core.UintegerValue (100));
    ns.core.Config.SetDefault ("ns3::PieQueueDisc::MinstrelPIE", ns.core.BooleanValue (isMinstrelPie))
    
    print "Install internet stack on all nodes."
    
    internet = ns.internet.InternetStackHelper()
    internet.Install(c)
    
    tchPfifo = ns.traffic_control.TrafficControlHelper()
    handle = tchPfifo.SetRootQueueDisc("ns3::PfifoFastQueueDisc")
    tchPfifo.AddInternalQueues (handle, 3, "ns3::DropTailQueue", "MaxPackets", ns.core.UintegerValue (1000));
    
    tchPie = ns.traffic_control.TrafficControlHelper()
    tchPie.SetRootQueueDisc ("ns3::PieQueueDisc")
    
    print "Create channels"
    
    p2p = ns.point_to_point.PointToPointHelper()
    
    devn0n2 = ns.network.NetDeviceContainer()
    devn1n2 = ns.network.NetDeviceContainer()
    devn2n3 = ns.network.NetDeviceContainer()
    devn3n4 = ns.network.NetDeviceContainer()
    devn3n5 = ns.network.NetDeviceContainer()
    
    queueDiscs = ns.traffic_control.QueueDiscContainer()
    
    p2p.SetQueue ("ns3::DropTailQueue");
    p2p.SetDeviceAttribute ("DataRate", ns.core.StringValue ("10Mbps"));
    p2p.SetChannelAttribute ("Delay", ns.core.StringValue ("2ms"));
    devn0n2 = p2p.Install (n0n2);
    tchPfifo.Install (devn0n2);
    
    p2p.SetQueue ("ns3::DropTailQueue");
    p2p.SetDeviceAttribute ("DataRate", ns.core.StringValue ("10Mbps"));
    p2p.SetChannelAttribute ("Delay", ns.core.StringValue ("3ms"));
    devn1n2 = p2p.Install (n1n2);
    tchPfifo.Install (devn1n2);
    
    p2p.SetQueue ("ns3::DropTailQueue");
    p2p.SetDeviceAttribute ("DataRate", ns.core.StringValue (pieLinkDataRate));
    p2p.SetChannelAttribute ("Delay", ns.core.StringValue (pieLinkDelay));
    devn2n3 = p2p.Install (n2n3);
    
    ## only backbone link has PIE queue disc
    queueDiscs = tchPie.Install (devn2n3);
    
    p2p.SetQueue ("ns3::DropTailQueue");
    p2p.SetDeviceAttribute ("DataRate", ns.core.StringValue ("10Mbps"));
    p2p.SetChannelAttribute ("Delay", ns.core.StringValue ("4ms"));
    devn3n4 = p2p.Install (n3n4);
    tchPfifo.Install (devn3n4);
    
    p2p.SetQueue ("ns3::DropTailQueue");
    p2p.SetDeviceAttribute ("DataRate", ns.core.StringValue ("10Mbps"));
    p2p.SetChannelAttribute ("Delay", ns.core.StringValue ("5ms"));
    devn3n5 = p2p.Install (n3n5);
    tchPfifo.Install (devn3n5);
    
    print "Assign IP Addressess"
    
    ipv4 = ns.internet.Ipv4AddressHelper()
    
    ipv4.SetBase(ns.network.Ipv4Address("10.1.1.0"),ns.network.Ipv4Mask("255.255.255.0"))
    i0i2 = ipv4.Assign (devn0n2)
    
    ipv4.SetBase(ns.network.Ipv4Address("10.1.2.0"),ns.network.Ipv4Mask("255.255.255.0"))
    i1i2 = ipv4.Assign (devn1n2)
    
    ipv4.SetBase(ns.network.Ipv4Address("10.1.3.0"),ns.network.Ipv4Mask("255.255.255.0"))
    i2i3 = ipv4.Assign (devn2n3)
    
    ipv4.SetBase(ns.network.Ipv4Address("10.1.4.0"),ns.network.Ipv4Mask("255.255.255.0"))
    i3i4 = ipv4.Assign (devn3n4)
    
    ipv4.SetBase(ns.network.Ipv4Address("10.1.5.0"),ns.network.Ipv4Mask("255.255.255.0"))
    i3i5 = ipv4.Assign (devn3n5)
    
    
    #set up the routing 
    ns.internet.Ipv4GlobalRoutingHelper.PopulateRoutingTables()
   
   
    
    def BuildAppsTest():
       #SINK is in the right side
	    port = 50000
	    address = ns.network.InetSocketAddress (ns.network.Ipv4Address.GetAny(), port)
	    
	    sinkHelper = ns.applications.PacketSinkHelper("ns3::TcpSocketFactory", address)
	    sinkApp = ns.network.ApplicationContainer()
	    
	    
	    sinkApp = sinkHelper.Install (n3n4.Get(1))
	    
	    sinkApp.Start (ns.core.Seconds (sink_start_time))
	    sinkApp.Stop (ns.core.Seconds (sink_stop_time))
	    
	    
	    #Connection 1
	    
	     # Clients are in left side
         
         # Create the OnOff applications to send TCP to the server
         # onoffhelper is a client that send data to TCP destination
           	    
	    clientHelper1 = ns.applications.OnOffHelper("ns3::TcpSocketFactory",ns.network.Address())
	    clientHelper1.SetAttribute ("OnTime", ns.core.StringValue ("ns3::ConstantRandomVariable[Constant=1]"))
	    clientHelper1.SetAttribute ("OffTime", ns.core.StringValue ("ns3::ConstantRandomVariable[Constant=0]"))
	    clientHelper1.SetAttribute ("PacketSize", ns.core.UintegerValue (1000))
	    clientHelper1.SetAttribute ("DataRate", ns.network.DataRateValue (ns.network.DataRate ("10Mb/s")))
	    
	    #Connection 2
	    clientHelper2 = ns.applications.OnOffHelper("ns3::TcpSocketFactory",ns.network.Address())
	    clientHelper2.SetAttribute ("OnTime", ns.core.StringValue ("ns3::ConstantRandomVariable[Constant=1]"))
	    clientHelper2.SetAttribute ("OffTime", ns.core.StringValue ("ns3::ConstantRandomVariable[Constant=0]"))
	    clientHelper2.SetAttribute ("PacketSize", ns.core.UintegerValue (1000))
	    clientHelper2.SetAttribute ("DataRate", ns.network.DataRateValue (ns.network.DataRate ("10Mb/s")))

	    clientApps1 = ns.network.ApplicationContainer()
	    remoteAddress = ns.network.AddressValue()
	    remoteAddress = ns.network.AddressValue(ns.network.InetSocketAddress(i3i4.GetAddress (1), port))
	    clientHelper1.SetAttribute ("Remote", remoteAddress)
	    clientApps1.Add (clientHelper1.Install (n0n2.Get (0)));
	    clientApps1.Start (ns.core.Seconds (client_start_time));
	    clientApps1.Stop (ns.core.Seconds (client_stop_time));
	    
	    clientApps2 = ns.network.ApplicationContainer()
	    remoteAddress = ns.network.AddressValue(ns.network.InetSocketAddress(i3i4.GetAddress (1), port))
	    clientHelper2.SetAttribute ("Remote", remoteAddress)
	    clientApps2.Add (clientHelper2.Install (n1n2.Get (0)));
	    clientApps2.Start (ns.core.Seconds (client_start_time));
	    clientApps2.Stop (ns.core.Seconds (client_stop_time));
	    
   
    BuildAppsTest ()
    
    if writePcap:
        ptp = ns.point_to_point.PointToPointHelper()
        print pathOut+"/pie"
        ptp.EnablePcapAll(c_str())
    
    if flowMonitor:
        flowmonHelper = ns.flow_monitor.FlowMonitorHelper
        flowmon = flowmonHelper.InstallAll()
    
    if writeForPlot:
        print pathOut+"/pie-queue-disc.plotme"
        print pathOut+"/pie-queue-disc_avg.plotme"
        
        queue = queueDiscs.Get(0)
        ns.core.Simulator.ScheduleNow(CheckQueueDiscSize, queue)
    
    ns.core.Simulator.Stop(ns.core.Seconds(sink_stop_time))
    ns.core.Simulator.Run()
    
    
    
    def CheckQueueDiscSize(queue):
        qSize = queue.GetQueueSize()
    
        avgQueueDiscSize = avgQueueDiscSize + qSize
        checkTimes = checkTimes + 1
    
        #check queue disc size every 1/100 of a second
        ns.core.Simulator.Schedule(ns.core.Seconds(0.01),ChecckQueueDiscSize, queue)
    
        print ns.core.Simulator.Now().GetSeconds()+" "+str(qsize)+"\n"
    
        print ns.core.Simulator.Now().GetSeconds()+" "+str(avgQueueDiscSize / checkTimes)+"\n"
    
        
    
    st = queueDiscs.Get(0).GetStats()
    
    if st.GetNDroppedPackets(ns.traffic_control.PieQueueDisc.FORCED_DROP) != 0:
        print "There should be no drops due to queue full\n"
        exit(1)
    
    if flowMonitor:
        stmp = pathOut + "/pie.flowmon"
        flowmon.SerializeToXmlFile (stmp.c_str(), 0, 0);
        
    if printPieStats:
        print "*** PIE stats from Node 2 queue ***"
        print "\t"+str( st.GetNDroppedPackets(ns.traffic_control.PieQueueDisc.UNFORCED_DROP) )+" drops due to prob mark"+"\n"
        print "\t"+str( st.GetNDroppedPackets(ns.traffic_control.PieQueueDisc.FORCED_DROP) )+" drops due to queue limits"+"\n"
        
    ns.core.Simulator.Destroy()
    
    


if __name__=="__main__":
    main(sys.argv)
