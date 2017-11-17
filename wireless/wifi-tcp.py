   # -*-  Mode: Python; -*-
# /*
#  * Copyright (c) 2015, IMDEA Networks Institute
#  * Copyright (c) 2017, NITK Surathkal
#  *
#  * This program is free software; you can redistribute it and/or modify
#  * it under the terms of the GNU General Public License version 2 as
#  * published by the Free Software Foundation;
#  *
#  * This program is distributed in the hope that it will be useful,
#  * but WITHOUT ANY WARRANTY; without even the implied warranty of
#  * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  * GNU General Public License for more details.
#  *
#  * You should have received a copy of the GNU General Public License
#  * along with this program; if not, write to the Free Software
#  * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#  *
#  * Author: Hany Assasa <hany.assasa@gmail.com>
#  * Ported to Python by: Elvis Menezes <menezeselvis7@gmail.com>
#                         Somnath Sarkar <somnath.k.sarkar@gmail.com>
#                         Mehul Sharma < mehul.sharma214@gmail.com>
#  *                      Mohit P. Tahiliani <tahiliani@nitk.edu.in>
 #
 # This is a simple example to test TCP over 802.11n (with MPDU aggregation enabled).
 #
 # Network topology:
 #
 #   Ap    STA
 #   #      #
 #   |      |
 #   n1     n2
 #
 # In this example, an HT station sends TCP packets to the access point.
 # We report the total throughput received during a window of 100ms.
 # The user can specify the application data rate and choose the variant
 # of TCP i.e. congestion control algorithm to use.
 #

import ns.applications
import ns.core
import ns.internet
import ns.mobility
import ns.  wifi


sink = ns.applications.PacketSink()
lastTotalRx = 0                     # The value of the last total received bytes 

def CalculateThroughput ():
  global lastTotalRx
  now = ns.core.Simulator.Now ()                                        # Return the simulator's virtual time. 
  cur = (sink.GetTotalRx () - lastTotalRx) *  8 / 1e5     # Convert Application RX Packets to MBits. 
  print "{}s:  {} Mbit/s".format(now.GetSeconds(),cur)
  lastTotalRx = sink.GetTotalRx ()
  ns.core.Simulator.Schedule (ns.core.MilliSeconds (100), CalculateThroughput)


def main (argv):
  global sink
  cmd = ns.core.CommandLine ()
  cmd.payloadSize = 1472                       # Transport layer payload size in bytes. 
  cmd.dataRate = "100Mbps"                  # Application layer datarate. 
  cmd.tcpVariant = "TcpNewReno"             # TCP variant type. 
  cmd.phyRate = "HtMcs7"                    # Physical layer bitrate. 
  cmd.simulationTime = 10                        # Simulation time in seconds. 
  cmd.pcapTracing = "False"                       # PCAP Tracing is enabled or not. 
  
  payloadSize = cmd.payloadSize
  dataRate = cmd.dataRate
  tcpVariant = cmd.tcpVariant
  phyRate = cmd.phyRate
  simulationTime = cmd.simulationTime
  pcapTracing = cmd.pcapTracing

  # Command line argument parser setup. 
  cmd.AddValue ("payloadSize", "Payload size in bytes")
  cmd.AddValue ("dataRate", "Application data ate")
  cmd.AddValue ("tcpVariant", "Transport protocol to use: TcpNewReno, "
                "TcpHybla, TcpHighSpeed, TcpHtcp, TcpVegas, TcpScalable, TcpVeno, "
                "TcpBic, TcpYeah, TcpIllinois, TcpWestwood, TcpWestwoodPlus, TcpLedbat ")
  cmd.AddValue ("phyRate", "Physical layer bitrate")
  cmd.AddValue ("simulationTime", "Simulation time in seconds")
  cmd.AddValue ("pcap", "Enable/disable PCAP Tracing")
  cmd.Parse (sys.argv)

  tcpVariant = "ns3::" + tcpVariant

  # No fragmentation and no RTS/CTS 
  ns.core.Config.SetDefault ("ns3::WifiRemoteStationManager::FragmentationThreshold", ns.core.StringValue ("999999"))
  ns.core.Config.SetDefault ("ns3::WifiRemoteStationManager::RtsCtsThreshold", ns.core.StringValue ("999999"))

  # Select TCP variant
  if tcpVariant == "ns3::TcpWestwoodPlus":
      #TcpWestwoodPlus is not an actual TypeId name we need TcpWestwood here
      ns.core.Config.SetDefault ("ns3::TcpL4Protocol::SocketType", ns.core.TypeIdValue (TcpWestwood.GetTypeId ()))
      # the default protocol type in ns3::TcpWestwood is WESTWOOD
      ns.core.Config.SetDefault ("ns3::TcpWestwood::ProtocolType", ns.core.EnumValue (TcpWestwood.WESTWOODPLUS))
  else:
      tcpTid = ns.core.TypeId()
      if (ns.core.TypeId.LookupByNameFailSafe (tcpVariant)) == "True":
          print "TypeId " + tcpVariant + " not found"
      ns.core.Config.SetDefault ("ns3::TcpL4Protocol::SocketType", ns.core.TypeIdValue (ns.core.TypeId.LookupByName (tcpVariant)))

  # Configure TCP Options 
  ns.core.Config.SetDefault ("ns3::TcpSocket::SegmentSize", ns.core.UintegerValue (payloadSize))

  wifiMac = ns.wifi.WifiMacHelper()
  wifiHelper = ns.wifi.WifiHelper()
  wifiHelper.SetStandard (ns.wifi.WIFI_PHY_STANDARD_80211n_5GHZ)

  # Set up Legacy Channel 
  wifiChannel = ns.wifi.YansWifiChannelHelper()
  wifiChannel.SetPropagationDelay ("ns3::ConstantSpeedPropagationDelayModel")
  wifiChannel.AddPropagationLoss ("ns3::FriisPropagationLossModel", "Frequency", ns.core.DoubleValue (5e9))

  # Setup Physical Layer 
  wifiPhy = ns.wifi.YansWifiPhyHelper.Default()
  wifiPhy.SetChannel (wifiChannel.Create ())
  wifiPhy.Set ("TxPowerStart", ns.core.DoubleValue (10.0))
  wifiPhy.Set ("TxPowerEnd", ns.core.DoubleValue (10.0))
  wifiPhy.Set ("TxPowerLevels", ns.core.UintegerValue (1))
  wifiPhy.Set ("TxGain", ns.core.DoubleValue (0))
  wifiPhy.Set ("RxGain", ns.core.DoubleValue (0))
  wifiPhy.Set ("RxNoiseFigure", ns.core.DoubleValue (10))
  wifiPhy.Set ("CcaMode1Threshold", ns.core.DoubleValue (-79))
  wifiPhy.Set ("EnergyDetectionThreshold", ns.core.DoubleValue (-79 + 3))
  wifiPhy.SetErrorRateModel ("ns3::YansErrorRateModel")
  wifiHelper.SetRemoteStationManager ("ns3::ConstantRateWifiManager",
                                      "DataMode", ns.core.StringValue (phyRate),
                                      "ControlMode", ns.core.StringValue ("HtMcs0"))

  networkNodes = ns.network.NodeContainer()
  networkNodes.Create (2)
  apWifiNode = networkNodes.Get (0)
  staWifiNode = networkNodes.Get (1)

  # Configure AP 
  ssid = ns.wifi.Ssid ("network")
  wifiMac.SetType ("ns3::ApWifiMac",
                   "Ssid", ns.wifi.SsidValue (ssid))

  apDevice = ns.network.NetDeviceContainer()
  apDevice = wifiHelper.Install (wifiPhy, wifiMac, apWifiNode)

  # Configure STA 
  wifiMac.SetType ("ns3::StaWifiMac",
                   "Ssid", ns.wifi.SsidValue (ssid))

  staDevices = ns.network.NetDeviceContainer()
  staDevices = wifiHelper.Install (wifiPhy, wifiMac, staWifiNode)

  # Mobility model 
  mobility = ns.mobility.MobilityHelper()
  positionAlloc = ns.mobility.ListPositionAllocator()
  positionAlloc.Add (ns.core.Vector (0.0, 0.0, 0.0))
  positionAlloc.Add (ns.core.Vector (1.0, 1.0, 0.0))

  mobility.SetPositionAllocator (positionAlloc)
  mobility.SetMobilityModel ("ns3::ConstantPositionMobilityModel")
  mobility.Install (apWifiNode)
  mobility.Install (staWifiNode)

  # Internet stack 
  stack = ns.internet.InternetStackHelper ()
  stack.Install (networkNodes)

  address = ns.internet.Ipv4AddressHelper ()
  address.SetBase (ns.network.Ipv4Address ("10.1.1.0"), ns.network.Ipv4Mask ("255.255.255.0"))
  apInterface = ns.internet.Ipv4InterfaceContainer()
  apInterface = address.Assign (apDevice)
  staInterface = ns.internet.Ipv4InterfaceContainer()
  staInterface = address.Assign (staDevices)

  # Populate routing table 
  ns.internet.Ipv4GlobalRoutingHelper.PopulateRoutingTables ()

  # Install TCP Receiver on the access point 
  sinkHelper = ns.applications.PacketSinkHelper ("ns3::TcpSocketFactory", ns.network.InetSocketAddress (ns.network.Ipv4Address.GetAny (), 9))
  sinkApp = ns.network.ApplicationContainer()
  sinkApp = sinkHelper.Install (apWifiNode)
  sink = sinkApp.Get (0)

  # Install TCP/UDP Transmitter on the station 
  server = ns.applications.OnOffHelper("ns3::TcpSocketFactory", (ns.network.InetSocketAddress (apInterface.GetAddress (0), 9)))
  server.SetAttribute ("PacketSize", ns.core.UintegerValue (payloadSize))
  server.SetAttribute ("OnTime", ns.core.StringValue ("ns3::ConstantRandomVariable[Constant=1]"))
  server.SetAttribute ("OffTime", ns.core.StringValue ("ns3::ConstantRandomVariable[Constant=0]"))
  server.SetAttribute ("DataRate", ns.network.DataRateValue (ns.network.DataRate (dataRate)))
  serverApp = ns.network.ApplicationContainer()
  serverApp = server.Install (staWifiNode)

  # Start Applications 
  sinkApp.Start (ns.core.Seconds (0.0))
  serverApp.Start (ns.core.Seconds (1.0))
  ns.core.Simulator.Schedule (ns.core.Seconds (1.1), CalculateThroughput)

  # Enable Traces 
  if pcapTracing == "True":
      wifiPhy.SetPcapDataLinkType (YansWifiPhyHelper.DLT_IEEE802_11_RADIO)
      wifiPhy.EnablePcap ("AccessPoint", apDevice)
      wifiPhy.EnablePcap ("Station", staDevices)

  # Start Simulation 
  ns.core.Simulator.Stop (ns.core.Seconds (simulationTime + 1))
  ns.core.Simulator.Run ()
  ns.core.Simulator.Destroy ()

  averageThroughput = ((sink.GetTotalRx () * 8) / (1e6  * simulationTime))
  if averageThroughput < 50:
      print "Obtained throughput is not in the expected boundaries!"
      exit ()
  print "Average throughput: {}Mbit/s\n".format(averageThroughput)
  
if __name__ == '__main__':
    import sys
    sys.exit (main (sys.argv))


