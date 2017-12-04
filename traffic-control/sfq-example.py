#/*
# * Copyright (c) 2017 NITK Surathkal
# *
# * This program is free software you can redistribute it and/or modify
# * it under the terms of the GNU General Public License version 2 as
# * published by the Free Software Foundation
# *
# * This program is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# * GNU General Public License for more details.
# *
# * You should have received a copy of the GNU General Public License
# * along with this program if not, write to the Free Software
# * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
# *
# * Authors: Aditya Katapadi Kamath <akamath1997@gmail.com>
# *          A Tarun Karthik <tarunkarthik999@gmail.com>
# *          Anuj Revankar <anujrevankar@gmail.com>
# *          Mohit P. Tahiliani <tahiliani@nitk.edu.in>
# */

# /** Network topology
# *
# *    10Mb/s, 2ms                            10Mb/s, 4ms
# * n0--------------|                    |---------------n4
# *                 |   1.5Mbps/s, 20ms  |
# *                 n2------------------n3
# *    10Mb/s, 3ms  |                    |    10Mb/s, 5ms
# * n1--------------|                    |---------------n5
# *
# *
# */

import ns.applications
import ns.core
import ns.network
import ns.point_to_point
import ns.internet
import ns.traffic_control
import ns.flow_monitor
import sys

checkTimes=0
avgQueueDiscSize=0.0

# The times
global_start_time=0.0
global_stop_time=0.0
sink_start_time=0.0
sink_stop_time=0.0
client_start_time=0.0
client_stop_time=0.0

#NodeContainer n0n2
n0n2 = ns.network.NodeContainer()
n1n2 = ns.network.NodeContainer()
n2n3 = ns.network.NodeContainer()
n3n4 = ns.network.NodeContainer()
n4n5 = ns.network.NodeContainer()

i0i2=ns.internet.Ipv4InterfaceContainer()
i1i2=ns.internet.Ipv4InterfaceContainer()
i2i3=ns.internet.Ipv4InterfaceContainer()
i3i4=ns.internet.Ipv4InterfaceContainer()
i4i5=ns.internet.Ipv4InterfaceContainer()

def BuildAppsTest ():
  # SINK is in the right side
  port = 50000
  sinkLocalAddress=ns.network.Address(ns.network.InetSocketAddress (ns.network.Ipv4Address.GetAny (), port))
  
  sinkHelper=ns.applications.PacketSinkHelper ("ns3::TcpSocketFactory", sinkLocalAddress)
  sinkApp = ns.network.ApplicationContainer()
  sinkHelper.Install (n3n4.Get (1))
  sinkApp.Start (ns.core.Seconds (sink_start_time))
  sinkApp.Stop (ns.core.Seconds (sink_stop_time))

  # Connection one
  # Clients are in left side
  '''/*
   * Create the OnOff applications to send TCP to the server
   * onoffhelper is a client that send data to TCP destination
  */'''
  clientHelper1=ns.applications.OnOffHelper ("ns3::UdpSocketFactory", ns.core.address())
  clientHelper1.SetAttribute ("OnTime", ns.core.StringValue ("ns3::ConstantRandomVariable  [Constant=1]"))
  clientHelper1.SetAttribute ("OffTime", ns.core.StringValue ("ns3::ConstantRandomVariable[Constant=0]"))
  clientHelper1.SetAttribute ("DataRate", ns.core.DataRateValue("15Mb/s"))
  clientHelper1.SetAttribute ("PacketSize", ns.core.UintegerValue (1000))

  # Connection two
  clientHelper2=ns.applications.OnOffHelper ("ns3::UdpSocketFactory", ns.core.address())
  clientHelper2.SetAttribute ("OnTime", ns.core.StringValue ("ns3::ConstantRandomVariable  [Constant=1]"))
  clientHelper2.SetAttribute ("OffTime", ns.core.StringValue ("ns3::ConstantRandomVariable[Constant=0]"))
  clientHelper2.SetAttribute ("DataRate", ns.core.DataRateValue("15Mb/s"))
  clientHelper2.SetAttribute ("PacketSize", ns.core.UintegerValue (1000))

  clientApps1=ns.network.ApplicationContainer ()
  remoteAddress = ns.network.AddressValue()
  remoteAddress = ns.network.AddressValue(ns.network.InetSocketAddress(i3i4.GetAddress (1), port))

  clientHelper1.SetAttribute ("Remote", remoteAddress)
  clientApps1.Add (clientHelper1.Install (n0n2.Get (0)))
  clientApps1.Start (ns.core.Seconds (client_start_time))
  clientApps1.Stop (ns.core.Seconds (client_stop_time))

  clientApps1=ns.network.ApplicationContainer () 
  clientHelper2.SetAttribute ("Remote", remoteAddress)
  clientApps2.Add (clientHelper1.Install (n1n2.Get (0)))
  clientApps2.Start (ns.core.Seconds (client_start_time))
  clientApps2.Stop (ns.core.Seconds (client_stop_time))


def main(argv):
  sfqLinkDataRate = "1.5Mbps"
  sfqLinkDelay = "20ms"

  pathOut="."
  writeForPlot = ""
  writePcap = ""
  flowMonitor = ""

  printSfqStats = True

  global_start_time = 0.0
  sink_start_time = global_start_time
  client_start_time = global_start_time + 1.5
  global_stop_time = 7.0
  sink_stop_time = global_stop_time + 3.0
  client_stop_time = global_stop_time - 2.0


  pathOut = "." # Current directory
  cmd = ns.core.CommandLine ()
  cmd.AddValue ("pathOut", "Path to save results from --writeForPlot/--writePcap/--writeFlowMonitor", pathOut)
  cmd.AddValue ("writeForPlot", "<0/1> to write results for plot (gnuplot)", writeForPlot)
  cmd.AddValue ("writePcap", "<0/1> to write results in pcapfile", writePcap)
  cmd.AddValue ("writeFlowMonitor", "<0/1> to enable Flow Monitor and write their results", flowMonitor)

  cmd.Parse (sys.argv)

  print ("Create nodes")
  c=ns.network.NodeContainer()
  c.Create (6)
  ns.core.Names.Add ( "N0", c.Get (0))
  ns.core.Names.Add ( "N1", c.Get (1))
  ns.core.Names.Add ( "N2", c.Get (2))
  ns.core.Names.Add ( "N3", c.Get (3))
  ns.core.Names.Add ( "N4", c.Get (4))
  ns.core.Names.Add ( "N5", c.Get (5))
  n0n2 = ns.network.NodeContainer (ns.network.NodeContainer(c.Get (0)), ns.network.NodeContainer(c.Get (2)))
  n1n2 = ns.network.NodeContainer (ns.network.NodeContainer(c.Get (1)), ns.network.NodeContainer(c.Get (2)))
  n2n3 = ns.network.NodeContainer (ns.network.NodeContainer(c.Get (2)), ns.network.NodeContainer(c.Get (3)))
  n3n4 = ns.network.NodeContainer (ns.network.NodeContainer(c.Get (3)), ns.network.NodeContainer(c.Get (4)))
  n3n5 = ns.network.NodeContainer (ns.network.NodeContainer(c.Get (3)), ns.network.NodeContainer(c.Get (5)))

  ns.core.Config.SetDefault ("ns3::TcpL4Protocol::SocketType", ns.core.StringValue ("ns3::TcpNewReno"))

  ns.core.Config.SetDefault ("ns3::TcpSocket::SegmentSize", ns.core.UintegerValue (1000 - 42))
  ns.core.Config.SetDefault ("ns3::TcpSocket::DelAckCount", ns.core.UintegerValue (1))
  ns.core.GlobalValue.Bind ("ChecksumEnabled", ns.core.BooleanValue (False))


  print ("Set SFQ params")
  ns.core.Config.SetDefault ("ns3::SfqQueueDisc::Interval", ns.core.StringValue ("100ms"))
  ns.core.Config.SetDefault ("ns3::SfqQueueDisc::Target", ns.core.StringValue ("5ms"))
  ns.core.Config.SetDefault ("ns3::SfqQueueDisc::PacketLimit", ns.core.UintegerValue (10 * 1024))
  ns.core.Config.SetDefault ("ns3::SfqQueueDisc::Flows", ns.core.UintegerValue (1024))
  ns.core.Config.SetDefault ("ns3::SfqQueueDisc::DropBatchSize", ns.core.UintegerValue (64))

  print ("Install internet stack on all nodes.")
  internet=ns.internet.InternetStackHelper ()
  internet.Install (c)

  tchPfifo=ns.traffic_control.TrafficControlHelper()
  handle = tchPfifo.SetRootQueueDisc ("ns3::PfifoFastQueueDisc")
  tchPfifo.AddInternalQueues (handle, 3, "ns3::DropTailQueue", "MaxPackets", UintegerValue (10 * 1024))

  tchSfq=ns.traffic_control.TrafficControlHelper()
  tchSfq.SetRootQueueDisc ("ns3::SfqQueueDisc")
  tchSfq.AddPacketFilter(handle,"ns3::SfqIpv4PacketFilter")
  tchSfq.AddPacketFilter(handle,"ns3::SfqIpv6PacketFilter")

  print("Create channels")

  p2p=ns.point_to_point.PointToPointHelper()

  devn0n2=ns.network.NetDeviceContainer()
  devn1n2=ns.network.NetDeviceContainer()
  devn2n3=ns.network.NetDeviceContainer()
  devn3n4ns.network.NetDeviceContainer()
  devn3n5ns.network.NetDeviceContainer()

  queueDiscs = ns.traffic_control.QueueDiscContainer()
  p2p.SetQueue ("ns3::DropTailQueue")

  p2p.SetDeviceAttribute("DataRate", ns.core.StringValue("10Mbps"))
  p2p.SetChannelAttribute("Delay", ns.core.StringValue("2ms"))
  devn0n2 = p2p.Install (n0n2)
  tchPfifo.Install (devn0n2)

  p2p.SetQueue ("ns3::DropTailQueue")
  p2p.SetDeviceAttribute ("DataRate", ns.core.StringValue ("10Mbps"))
  p2p.SetChannelAttribute ("Delay", ns.core.StringValue ("3ms"))
  devn1n2 = p2p.Install (n1n2)
  tchPfifo.Install (devn1n2)

  p2p.SetQueue ("ns3::DropTailQueue")
  p2p.SetDeviceAttribute ("DataRate", ns.core.StringValue (sfqLinkDataRate))
  p2p.SetChannelAttribute ("Delay", ns.core.StringValue (sfqLinkDelay))
  devn2n3 = p2p.Install (n2n3)

  queueDiscs = tchSfq.Install (devn2n3)

  p2p.SetQueue ("ns3::DropTailQueue")
  p2p.SetDeviceAttribute ("DataRate", ns.core.StringValue ("10Mbps"))
  p2p.SetChannelAttribute ("Delay", ns.core.StringValue ("4ms"))
  devn3n4 = p2p.Install (n3n4)
  tchPfifo.Install (devn3n4)

  p2p.SetQueue ("ns3::DropTailQueue")
  p2p.SetDeviceAttribute ("DataRate", ns.core.StringValue ("10Mbps"))
  p2p.SetChannelAttribute ("Delay", ns.core.StringValue ("5ms"))
  devn3n5 = p2p.Install (n3n5)
  tchPfifo.Install (devn3n5)

  print("Assign IP Addresses")

  ipv4=ns.internet.Ipv4AddressHelper()

  ipv4.SetBase(ns.network.Ipv4Address("10.1.1.0"),ns.network.Ipv4Mask("255.255.255.0"))

  i0i2 = ipv4.Assign(devn0n2)      


  ipv4.SetBase(ns.network.Ipv4Address("10.1.2.0"),ns.network.Ipv4Mask("255.255.255.0"))
  i1i2 = ipv4.Assign (devn1n2)


  ipv4.SetBase(ns.network.Ipv4Address("10.1.3.0"),ns.network.Ipv4Mask("255.255.255.0"))
  i2i3 = ipv4.Assign (devn2n3)


  ipv4.SetBase(ns.network.Ipv4Address("10.1.4.0"),ns.network.Ipv4Mask("255.255.255.0"))
  i3i4 = ipv4.Assign (devn3n4)


  ipv4.SetBase(ns.network.Ipv4Address("10.1.5.0"),ns.network.Ipv4Mask("255.255.255.0"))
  i3i5 = ipv4.Assign (devn3n5)

  ns.internet.Ipv4GlobalRoutingHelper.PopulateRoutingTables()
  BuildAppsTest ()

  if (writePcap):
    ptp=ns.point_to_point.PointToPointHelper()
    print pathOut+"/sfq"
    ptp.EnablePcapAll(c_str())    

  if (flowMonitor):
    flowmonHelper = ns.flow_monitor.FlowMonitorHelper
    flowmon = flowmonHelper.InstallAll()

  if (writeForPlot):
    print pathOut+"/sfq-queue-disc.plotme"
    print pathOut+"/sfq-queue-disc_avg.plotme"
    queue = queueDiscs.Get (0)

  ns.core.Simulator.Stop (ns.core.Seconds (sink_stop_time))
  ns.core.Simulator.Run()
  st = ns.traffic_control.QueueDisc.Stats()
  st = queueDiscs.Get(0).GetStats ()

  if (flowMonitor):
    stmp = pathOut + "/pie.flowmon"
    flowmon.SerializeToXmlFile (stmp.c_str(), False, False)
  ns.core.Simulator.Destroy()

if __name__ == '__main__':
    main(sys.argv)

