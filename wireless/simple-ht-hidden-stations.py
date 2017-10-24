# -*-  Mode: Python; -*-
# /*
#  * Copyright (c) 2015 Sebastien Deronne
#  * Copyright (c) 2016 NITK Surathkal
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
#  * Author: Sebastien Deronne <sebastien.deronne@gmail.com>
#  * Ported to Python by: Kavya Sree Bhagavatula <kavyasbhagavatula@gmail.com>
#  *                      Shrishti <shrishtiak26894@gmail.com>
#  */

import ns.core
import ns.applications
import ns.wifi
import ns.mobility
import ns.internet

# This example considers two hidden stations in an 802.11n network which supports MPDU aggregation.
# The user can specify whether RTS/CTS is used and can set the number of aggregated MPDUs.
#
# Example: ./waf --pyrun "examples/wireless/simple-ht-hidden-stations.py --enableRts=True --nMpdus=8"
#
# Network topology:
#
#   Wifi 192.168.1.0
#
#        AP
#   *    *    *
#   |    |    |
#   n1   n2   n3
#
# Packets in this simulation aren't marked with a QosTag so they are considered
# belonging to BestEffort Access Class (AC_BE).

def main (argv):
	cmd = ns.core.CommandLine ()
	cmd.payloadSize = 1472 # bytes
	cmd.simulationTime = 10 # seconds
	cmd.nMpdus = 1
	cmd.maxAmpduSize = 0
	cmd.enableRts = "False"
	cmd.minExpectedThroughput = 0
	cmd.maxExpectedThroughput = 0
    	
	cmd.AddValue ("nMpdus", "Number of aggregated MPDUs")
	cmd.AddValue ("payloadSize", "Payload size in bytes")
	cmd.AddValue ("enableRts", "Enable RTS/CTS")
	cmd.AddValue ("simulationTime", "Simulation time in seconds")
	cmd.AddValue ("minExpectedThroughput", "if set, simulation fails if the lowest throughput is below this value")
	cmd.AddValue ("maxExpectedThroughput", "if set, simulation fails if the highest throughput is above this value")
	cmd.Parse (sys.argv)

	payloadSize = int (cmd.payloadSize)
	simulationTime = float (cmd.simulationTime)
	nMpdus = int (cmd.nMpdus)
	maxAmpduSize = int (cmd.maxAmpduSize)
	enableRts = cmd.enableRts
	minExpectedThroughput = cmd.minExpectedThroughput
	maxExpectedThroughput = cmd.maxExpectedThroughput
	
	if enableRts == "False":
		ns.core.Config.SetDefault ("ns3::WifiRemoteStationManager::RtsCtsThreshold", ns.core.StringValue ("999999"))	
	else:
		ns.core.Config.SetDefault ("ns3::WifiRemoteStationManager::RtsCtsThreshold", ns.core.StringValue ("0"))    
     
  	ns.core.Config.SetDefault ("ns3::WifiRemoteStationManager::FragmentationThreshold", ns.core.StringValue ("990000"))

  	# Set the maximum size for A-MPDU with regards to the payload size
  	maxAmpduSize = nMpdus * (payloadSize + 200)

  	# Set the maximum wireless range to 5 meters in order to reproduce a hidden nodes scenario, i.e. the distance between hidden stations is larger 	than 5 meters
  	ns.core.Config.SetDefault ("ns3::RangePropagationLossModel::MaxRange", ns.core.DoubleValue (5))

	wifiStaNodes = ns.network.NodeContainer ()
	wifiStaNodes.Create (2)
	wifiApNode = ns.network.NodeContainer ()
	wifiApNode.Create (1)
	
	channel = ns.wifi.YansWifiChannelHelper.Default ()
	channel.AddPropagationLoss ("ns3::RangePropagationLossModel") # wireless range limited to 5 meters!

	phy = ns.wifi.YansWifiPhyHelper.Default ()
	phy.SetPcapDataLinkType (ns.wifi.YansWifiPhyHelper.DLT_IEEE802_11_RADIO)
	phy.SetChannel (channel.Create ())

	wifi = ns.wifi.WifiHelper.Default ()
	wifi.SetStandard (ns.wifi.WIFI_PHY_STANDARD_80211n_5GHZ)
	wifi.SetRemoteStationManager ("ns3::ConstantRateWifiManager", "DataMode", ns.core.StringValue ("HtMcs7"), "ControlMode", ns.core.StringValue ("HtMcs0"))
	mac = ns.wifi.HtWifiMacHelper.Default ()

	ssid = ns.wifi.Ssid ("simple-mpdu-aggregation")
	mac.SetType ("ns3::StaWifiMac",
				"Ssid", ns.wifi.SsidValue (ssid),
				"ActiveProbing", ns.core.BooleanValue (False),
				"BE_MaxAmpduSize", ns.core.UintegerValue (maxAmpduSize))

	staDevices = ns.network.NetDeviceContainer ()
	staDevices = wifi.Install (phy, mac, wifiStaNodes)

	mac.SetType ("ns3::ApWifiMac",
				"Ssid", ns.wifi.SsidValue (ssid),
				"EnableBeaconJitter", ns.core.BooleanValue (False),
				"BE_MaxAmpduSize", ns.core.UintegerValue (maxAmpduSize))

	apDevice = ns.network.NetDeviceContainer ()
 	apDevice = wifi.Install (phy, mac, wifiApNode)

	mobility = ns.mobility.MobilityHelper ()
	positionAlloc = ns.mobility.ListPositionAllocator ()

	positionAlloc.Add (ns.core.Vector3D (5.0, 0.0, 0.0))
	positionAlloc.Add (ns.core.Vector3D (0.0, 0.0, 0.0))
	positionAlloc.Add (ns.core.Vector3D (10.0, 0.0, 0.0))
	mobility.SetPositionAllocator (positionAlloc)

	mobility.SetMobilityModel ("ns3::ConstantPositionMobilityModel")
	mobility.Install (wifiApNode)
	mobility.Install (wifiStaNodes)

	stack = ns.internet.InternetStackHelper ()
	stack.Install (wifiApNode)
	stack.Install (wifiStaNodes)

	address = ns.internet.Ipv4AddressHelper ()
	address.SetBase (ns.network.Ipv4Address ("192.168.1.0"), ns.network.Ipv4Mask ("255.255.255.0"))
	StaInterface = ns.internet.Ipv4InterfaceContainer ()
	StaInterface = address.Assign (staDevices)
	ApInterface = ns.internet.Ipv4InterfaceContainer ()
	ApInterface = address.Assign (apDevice)

	port = 9 
	server = ns.applications.UdpServerHelper (port)
	serverApp = server.Install (wifiApNode)
	serverApp.Start (ns.core.Seconds (0.0))
	serverApp.Stop (ns.core.Seconds (simulationTime + 1))
      
	client = ns.applications.UdpClientHelper (ApInterface.GetAddress (0), port)
	client.SetAttribute ("MaxPackets", ns.core.UintegerValue (4294967295))
	client.SetAttribute ("Interval", ns.core.TimeValue (ns.core.Time ("0.00002")))
	client.SetAttribute ("PacketSize", ns.core.UintegerValue (payloadSize))
  
	clientApp1 = client.Install (wifiStaNodes)
	clientApp1.Start (ns.core.Seconds (1.0))
	clientApp1.Stop (ns.core.Seconds (simulationTime + 1))
  
	phy.EnablePcap ("SimpleHtHiddenStations_py_Ap", apDevice.Get (0))
	phy.EnablePcap ("SimpleHtHiddenStations_py_Sta1", staDevices.Get (0))
	phy.EnablePcap ("SimpleHtHiddenStations_py_Sta2", staDevices.Get (1))
      
	ns.core.Simulator.Stop (ns.core.Seconds (simulationTime + 1))

	ns.core.Simulator.Run ()
	ns.core.Simulator.Destroy ()
      
	totalPacketsThrough = serverApp.Get (0).GetReceived ()
	throughput = totalPacketsThrough * payloadSize * 8 / (simulationTime * 1000000.0)
	print "Throughput:", throughput,"Mbit/s"
  
	if (throughput < minExpectedThroughput or (maxExpectedThroughput > 0 and throughput > maxExpectedThroughput)):
		print "Obtained throughput:", throughput,"is not in the expected boundaries!",'\n'
		exit (1)

	return 0

if __name__ == '__main__':
    import sys
    sys.exit (main (sys.argv))
