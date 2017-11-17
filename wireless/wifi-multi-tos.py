# -*-  Mode: C++; c-file-style: "gnu"; indent-tabs-mode:nil; -*- */
#
 # Copyright (c) 2016
 # Copyright (c) 2017, NITK Surathkal
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
 # Author: Sebastien Deronne <sebastien.deronne@gmail.com>
 #  * Ported to Python by: Elvis Menezes <menezeselvis7@gmail.com>
 #                         Somnath Sarkar <somnath.k.sarkar@gmail.com>
 #                         Mehul Sharma < mehul.sharma214@gmail.com>
 #  *                      Mohit P. Tahiliani <tahiliani@nitk.edu.in>
 #/

import ns.core
import ns.applications
import ns.wifi
import ns.mobility
import ns.internet

# This is a simple example in order to show how to configure an IEEE 802.11n Wi-Fi network
# with multiple TOS. It outputs the aggregated UDP throughput, which depends on the number of
# stations, the HT MCS value (0 to 7), the channel width (20 or 40 MHz) and the guard interval
# (long or short). The user can also specify the distance between the access point and the
# stations (in meters), and can specify whether RTS/CTS is used or not.


def main(argv):
  cmd = ns.core.CommandLine ()
  cmd.nWifi = 4
  cmd.simulationTime = 10 #seconds
  cmd.distance = 1.0 #meters
  cmd.mcs = 7
  cmd.channelWidth = 20 #MHz
  cmd.useShortGuardInterval = "False"
  cmd.useRts = "False"
  cmd.AddValue ("nWifi", "Number of stations")
  cmd.AddValue ("distance", "Distance in meters between the stations and the access point")
  cmd.AddValue ("simulationTime", "Simulation time in seconds")
  cmd.AddValue ("useRts", "Enable/disable RTS/CTS")
  cmd.AddValue ("mcs", "MCS value (0 - 7)")
  cmd.AddValue ("channelWidth", "Channel width in MHz")
  cmd.AddValue ("useShortGuardInterval", "Enable/disable short guard interval")
  cmd.Parse (sys.argv)

  nWifi = cmd.nWifi
  simulationTime = cmd.simulationTime
  distance = cmd.distance
  mcs = cmd.mcs 
  channelWidth = cmd.channelWidth
  useShortGuardInterval = cmd.useShortGuardInterval 
  useRts = cmd.useRts

  wifiStaNodes = ns.network.NodeContainer()
  wifiStaNodes.Create (nWifi)
  wifiApNode = ns.network.NodeContainer()
  wifiApNode.Create (1)

  channel = ns.wifi.YansWifiChannelHelper()
  channel = ns.wifi.YansWifiChannelHelper.Default ()
  phy = ns.wifi.YansWifiPhyHelper()
  phy = ns.wifi.YansWifiPhyHelper.Default ()
  phy.SetChannel (channel.Create ())

  # Set guard interval
  phy.Set ("ShortGuardEnabled", ns.core.BooleanValue (useShortGuardInterval))

  mac = ns.wifi.WifiMacHelper()
  wifi = ns.wifi.WifiHelper()
  wifi.SetStandard (ns.wifi.WIFI_PHY_STANDARD_80211n_5GHZ)
  
  if useRts == "False":
      thresh = 999999
  else:
      thresh = 0
  wifi.SetRemoteStationManager ("ns3::ConstantRateWifiManager",
                                "DataMode", ns.core.StringValue ("HtMcs{}".format(mcs)),
                                "ControlMode", ns.core.StringValue ("HtMcs{}".format(mcs)),
                                "RtsCtsThreshold", ns.core.UintegerValue (thresh))

  ssid = ns.wifi.Ssid("ns3-80211n")

  mac.SetType ("ns3::StaWifiMac",
               "Ssid", ns.wifi.SsidValue (ssid))

  staDevices = ns.network.NetDeviceContainer()
  staDevices = wifi.Install (phy, mac, wifiStaNodes)

  mac.SetType ("ns3::ApWifiMac",
               "Ssid", ns.wifi.SsidValue (ssid))

  apDevice = ns.network.NetDeviceContainer()
  apDevice = wifi.Install (phy, mac, wifiApNode)

  # Set channel width
  ns.core.Config.Set ("/NodeList#/DeviceList#/$ns3::WifiNetDevice/Phy/ChannelWidth", ns.core.UintegerValue (channelWidth))

  # mobility
  mobility = ns.mobility.MobilityHelper()
  positionAlloc = ns.mobility.ListPositionAllocator()
  positionAlloc.Add (ns.core.Vector (0.0, 0.0, 0.0))
  for i in range(0,nWifi):
      positionAlloc.Add (ns.core.Vector (distance, 0.0, 0.0))
  mobility.SetPositionAllocator (positionAlloc)
  mobility.SetMobilityModel ("ns3::ConstantPositionMobilityModel")
  mobility.Install (wifiApNode)
  mobility.Install (wifiStaNodes)

  # Internet stack
  stack = ns.internet.InternetStackHelper ()
  stack.Install (wifiApNode)
  stack.Install (wifiStaNodes)

  address = ns.internet.Ipv4AddressHelper()
  address.SetBase (ns.network.Ipv4Address ("10.1.1.0"), ns.network.Ipv4Mask ("255.255.255.0"))

  apNodeInterface = ns.internet.Ipv4InterfaceContainer()
  staNodeInterfaces = ns.internet.Ipv4InterfaceContainer()
  staNodeInterfaces = address.Assign (staDevices)
  apNodeInterface = address.Assign (apDevice)

  # Setting applications
  sourceApplications = ns.network.ApplicationContainer()
  sinkApplications = ns.network.ApplicationContainer()
  tosValues = {0x70, 0x28, 0xb8, 0xc0} #AC_BE, AC_BK, AC_VI, AC_VO
  port = 9
  for index in range(0,nWifi):
      for tosValue in (tosValues):
          ipv4 = wifiApNode.Get (0).GetObject(ns.internet.Ipv4.GetTypeId())
          address = ipv4.GetAddress (1, 0).GetLocal ()
          sinkSocket = ns.network.InetSocketAddress(address,port)
          port = port+1
          sinkSocket.SetTos (tosValue)

          onOffHelper = ns.applications.OnOffHelper ("ns3::UdpSocketFactory", sinkSocket)
          onOffHelper.SetAttribute ("OnTime", ns.core.StringValue ("ns3::ConstantRandomVariable[Constant=1]"))
          onOffHelper.SetAttribute ("OffTime", ns.core.StringValue ("ns3::ConstantRandomVariable[Constant=0]"))
          onOffHelper.SetAttribute ("DataRate", ns.network.DataRateValue (ns.network.DataRate(50000000 / nWifi)))
          onOffHelper.SetAttribute ("PacketSize", ns.core.UintegerValue (1472)) #bytes
          sourceApplications.Add (onOffHelper.Install (wifiStaNodes.Get (index)))
          packetSinkHelper = ns.applications.PacketSinkHelper ("ns3::UdpSocketFactory",sinkSocket)
          sinkApplications.Add (packetSinkHelper.Install (wifiApNode.Get (0)))
        

  sinkApplications.Start (ns.core.Seconds (0.0))
  sinkApplications.Stop (ns.core.Seconds (simulationTime + 1))
  sourceApplications.Start (ns.core.Seconds (1.0))
  sourceApplications.Stop (ns.core.Seconds (simulationTime + 1))

  ns.internet.Ipv4GlobalRoutingHelper.PopulateRoutingTables ()

  ns.core.Simulator.Stop(ns.core.Seconds (simulationTime + 1))
  ns.core.Simulator.Run ()
  ns.core.Simulator.Destroy ()

  throughput = 0
  for index in range(0,sinkApplications.GetN()):
      totalPacketsThrough = (sinkApplications.Get (index)).GetTotalRx ()
      throughput += ((totalPacketsThrough * 8) / (simulationTime * 1000000.0)) #Mbit/s
  if (throughput > 0):
      print "Aggregated throughput: {} Mbit/s".format(throughput)
  else:
      print "Obtained throughput is 0!"
      exit()

if __name__ == '__main__':
    import sys
    sys.exit (main (sys.argv))