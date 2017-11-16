#Team Member : Siddhartha Chowdhuri (15CO246), Atul Singh (15CO151), Aswin Manoj (15CO209).

import sys
import ns.core
import ns.network
import ns.internet
import ns.point_to_point
import ns.applications
import ns.point_to_point_layout
import ns.traffic_control    

def main(argv):

    cmd = ns.core.CommandLine ()

    cmd.nLeaf = 10
    cmd.maxPackets = 100
    cmd.modeBytes  = "False"
    cmd.queueDiscLimitPackets = 1000
    cmd.minTh = 5
    cmd.maxTh = 15
    cmd.pktSize = 512
    cmd.appDataRate = "10Mbps"
    cmd.queueDiscType = "RED"
    cmd.port = 5001
    cmd.bottleNeckLinkBw = "1Mbps"
    cmd.bottleNeckLinkDelay = "50ms"
    cmd.AddValue ("nLeaf","Number of left and right side leaf nodes")
    cmd.AddValue ("maxPackets","Max Packets allowed in the device queue");
    cmd.AddValue ("queueDiscLimitPackets","Max Packets allowed in the queue disc")
    cmd.AddValue ("queueDiscType", "Set Queue disc type to RED or NLRED")
    cmd.AddValue ("appPktSize", "Set OnOff App Packet Size")
    cmd.AddValue ("appDataRate", "Set OnOff App DataRate")
    cmd.AddValue ("modeBytes", "Set Queue disc mode to Packets <false> or bytes <true>")
    cmd.AddValue ("redMinTh", "RED queue minimum threshold")
    cmd.AddValue ("redMaxTh", "RED queue maximum threshold")
    cmd.Parse (sys.argv)


    if((cmd.queueDiscType != "RED") and (cmd.queueDiscType != "NLRED")):
        print ("Invalid queue disc type: Use --queueDiscType=RED or --queueDiscType=NLRED")
        sys.exit(1)

    ns.core.Config.SetDefault ("ns3::OnOffApplication::PacketSize", ns.core.UintegerValue (cmd.pktSize))
    ns.core.Config.SetDefault ("ns3::OnOffApplication::DataRate", ns.core.StringValue (cmd.appDataRate))
    ns.core.Config.SetDefault ("ns3::QueueBase::Mode", ns.core.StringValue ("QUEUE_MODE_PACKETS"))
    ns.core.Config.SetDefault ("ns3::QueueBase::MaxPackets", ns.core.UintegerValue (cmd.maxPackets))

    if (cmd.modeBytes != 1): #check this once more.
      ns.core.Config.SetDefault ("ns3::RedQueueDisc::Mode", ns.core.StringValue ("QUEUE_DISC_MODE_PACKETS"))
      ns.core.Config.SetDefault ("ns3::RedQueueDisc::QueueLimit", ns.core.UintegerValue (cmd.queueDiscLimitPackets))

    else:
      ns.core.Config.SetDefault ("ns3::RedQueueDisc::Mode", ns.core.StringValue ("QUEUE_DISC_MODE_BYTES"))
      ns.core.Config.SetDefault ("ns3::RedQueueDisc::QueueLimit", ns.core.UintegerValue (cmd.queueDiscLimitPackets * cmd.pktSize))
      cmd.minTh *= cmd.pktSize
      cmd.maxTh *= cmd.pktSize

    ns.core.Config.SetDefault ("ns3::RedQueueDisc::MinTh", ns.core.DoubleValue (cmd.minTh))
    ns.core.Config.SetDefault ("ns3::RedQueueDisc::MaxTh", ns.core.DoubleValue (cmd.maxTh))
    ns.core.Config.SetDefault ("ns3::RedQueueDisc::LinkBandwidth", ns.core.StringValue (cmd.bottleNeckLinkBw))
    ns.core.Config.SetDefault ("ns3::RedQueueDisc::LinkDelay", ns.core.StringValue (cmd.bottleNeckLinkDelay))
    ns.core.Config.SetDefault ("ns3::RedQueueDisc::MeanPktSize", ns.core.UintegerValue (cmd.pktSize))

    if (cmd.queueDiscType == "NLRED"):
      # Turn on NLRED
      ns.core.Config.SetDefault ("ns3::RedQueueDisc::NLRED", BooleanValue (True))
    
    bottleNeckLink = ns.point_to_point.PointToPointHelper()

    #Create the point-to-point link helpers

    bottleNeckLink.SetDeviceAttribute  ("DataRate", ns.core.StringValue(cmd.bottleNeckLinkBw))
    bottleNeckLink.SetChannelAttribute ("Delay", ns.core.StringValue (cmd.bottleNeckLinkDelay))

    pointToPointLeaf = ns.point_to_point.PointToPointHelper()

    pointToPointLeaf.SetDeviceAttribute("DataRate", ns.core.StringValue ("10Mbps"))
    pointToPointLeaf.SetChannelAttribute("Delay", ns.core.StringValue ("1ms"))

    d = ns.point_to_point_layout.PointToPointDumbbellHelper(cmd.nLeaf, pointToPointLeaf,cmd.nLeaf, pointToPointLeaf,bottleNeckLink)

    # Install Stack.
    stack = ns.internet.InternetStackHelper()

    for i in xrange(d.LeftCount()):
      stack.Install (d.GetLeft(i))

    for i in xrange(d.RightCount()):
        stack.Install (d.GetRight(i))

    stack.Install (d.GetLeft())
    stack.Install (d.GetRight())

    tchBottleneck = ns.traffic_control.TrafficControlHelper()
    queueDiscs    = ns.traffic_control.QueueDiscContainer()
    tchBottleneck.SetRootQueueDisc ("ns3::RedQueueDisc")
    tchBottleneck.Install(d.GetLeft().GetDevice(0))
    queueDiscs = tchBottleneck.Install(d.GetRight().GetDevice (0));

    # Assign IP Addresses
    d.AssignIpv4Addresses (ns.internet.Ipv4AddressHelper (ns.network.Ipv4Address("10.1.1.0"),ns.network.Ipv4Mask("255.255.255.0")), 
    ns.internet.Ipv4AddressHelper (ns.network.Ipv4Address("10.2.1.0"),ns.network.Ipv4Mask("255.255.255.0")),
    ns.internet.Ipv4AddressHelper (ns.network.Ipv4Address("10.3.1.0"),ns.network.Ipv4Mask("255.255.255.0")))

    # Install on/off app on all right side nodes
    clientHelper = ns.applications.OnOffHelper ("ns3::TcpSocketFactory", ns.network.Address ())
    clientHelper.SetAttribute ("OnTime", ns.core.StringValue ("ns3::UniformRandomVariable[Min=0.|Max=1.]"))
    clientHelper.SetAttribute ("OffTime", ns.core.StringValue ("ns3::UniformRandomVariable[Min=0.|Max=1.]"))

    sinkLocalAddress = ns.network.Address (ns.network.InetSocketAddress (ns.network.Ipv4Address.GetAny(),cmd.port))
    packetSinkHelper = ns.applications.PacketSinkHelper ("ns3::TcpSocketFactory", sinkLocalAddress);
    sinkApps = ns.network.ApplicationContainer ();

    for i in xrange(d.LeftCount()):
        sinkApps.Add(packetSinkHelper.Install(d.GetLeft(i)))

    sinkApps.Start (ns.core.Seconds(0.0));
    sinkApps.Stop  (ns.core.Seconds(30.0));

    clientApps = ns.network.ApplicationContainer()

    for i in xrange(d.RightCount()):
        #Create an on/off app sending packets to the left side
        remoteAddress = ns.network.AddressValue (ns.network.InetSocketAddress (d.GetLeftIpv4Address(i),cmd.port))
        clientHelper.SetAttribute ("Remote", remoteAddress)
        clientApps.Add (clientHelper.Install (d.GetRight(i)))

    clientApps.Start (ns.core.Seconds(1.0));    #Start 1 second after sink
    clientApps.Stop  (ns.core.Seconds(15.0));   #Stop before the sink

    ns.internet.Ipv4GlobalRoutingHelper.PopulateRoutingTables()

    print("Running the simulation\n")

    ns.core.Simulator.Run()

    st = queueDiscs.Get(0).GetStats()

    if (st.GetNDroppedPackets (ns.traffic_control.RedQueueDisc.UNFORCED_DROP) == 0):
        print("There should be some unforced drops\n")
        sys.exit (1);

    if (st.GetNDroppedPackets (ns.traffic_control.QueueDisc.INTERNAL_QUEUE_DROP) != 0):
        print("There should be zero drops due to queue full\n")
        sys.exit (1);

    print("*** Stats from the bottleneck queue disc ***\n")
    print(st)
    print("\nDestroying the simulation\n")

if __name__ == '__main__':
    main (sys.argv)

    
  
