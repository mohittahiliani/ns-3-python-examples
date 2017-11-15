
import ns.core
import ns.network
import ns.applications
import ns.wifi
import ns.mobility
import ns.internet

def main(argv):
  	payloadSize = 1472
  	simulationTime = 10
	distance = 5 
	enablePcap = 1

  
	cmd = ns.core.CommandLine ()
	cmd.AddValue ("payloadSize", "Payload size in bytes")
 	cmd.AddValue ("simulationTime", "Simulation time in seconds")
	cmd.AddValue ("distance", "Distance in meters between the station and the access point")
	cmd.AddValue ("enablePcap", "Enable/disable pcap file generation")
	cmd.Parse (sys.argv)



	wifiStaNode = ns.network.NodeContainer ()
        wifiStaNode.Create (4)
        wifiApNode = ns.network.NodeContainer ()
	wifiApNode.Create (4)

	channel = ns.wifi.YansWifiChannelHelper.Default ()
	phy = ns.wifi.YansWifiPhyHelper.Default ()
	phy.SetPcapDataLinkType (ns.wifi.YansWifiPhyHelper.DLT_IEEE802_11_RADIO)
	phy.SetChannel (channel.Create ())

	wifi = ns.wifi.WifiHelper.Default ()
	wifi.SetStandard (ns.wifi.WIFI_PHY_STANDARD_80211n_5GHZ)
	wifi.SetRemoteStationManager ("ns3::ConstantRateWifiManager", 
					"DataMode", ns.core.StringValue ("HtMcs7"), 		
					"ControlMode", ns.core.StringValue("HtMcs0"))
	mac = ns.wifi.HtWifiMacHelper.Default ()
  
  	#Ssid ssid;

	staDevicesA = ns.network.NetDeviceContainer ()
	staDevicesB = ns.network.NetDeviceContainer ()
	staDevicesC = ns.network.NetDeviceContainer ()
	staDevicesD = ns.network.NetDeviceContainer ()

	apDeviceA = ns.network.NetDeviceContainer ()
	apDeviceB = ns.network.NetDeviceContainer ()
	apDeviceC = ns.network.NetDeviceContainer ()
	apDeviceD = ns.network.NetDeviceContainer ()

	# Network A
	ssid = ns.wifi.Ssid ("network-A")

	phy.Set ("ChannelNumber", ns.core.UintegerValue (36))
	mac.SetType ("ns3::StaWifiMac","Ssid", ns.wifi.SsidValue (ssid))
	staDeviceA = wifi.Install (phy, mac, wifiStaNode.Get(0))
	mac.SetType ("ns3::ApWifiMac", "Ssid", ns.wifi.SsidValue (ssid), "BeaconGeneration", ns.core.BooleanValue (True))
	apDeviceA = wifi.Install (phy, mac, wifiApNode.Get(0))
  
	# Network B
	ssid = ns.wifi.Ssid ("network-B")

	phy.Set ("ChannelNumber", ns.core.UintegerValue(40))
	mac.SetType ("ns3::StaWifiMac", "Ssid", ns.wifi.SsidValue (ssid), "BE_MaxAmpduSize", ns.core.UintegerValue (0))
	staDeviceB = wifi.Install (phy, mac, wifiStaNode.Get(1))
	mac.SetType ("ns3::ApWifiMac", "Ssid", ns.wifi.SsidValue (ssid), "BeaconGeneration", ns.core.BooleanValue (True))
	apDeviceB = wifi.Install (phy, mac, wifiApNode.Get(1))
	  
	  
	# Network C
	ssid = ns.wifi.Ssid ("network-C")

	phy.Set ("ChannelNumber", ns.core.UintegerValue(44))
	mac.SetType ("ns3::StaWifiMac", "Ssid", ns.wifi.SsidValue (ssid), "BE_MaxAmpduSize", ns.core.UintegerValue (0),"BE_MaxAmsduSize", ns.core.UintegerValue (7935))
	staDeviceC = wifi.Install (phy, mac, wifiStaNode.Get(2))
	mac.SetType ("ns3::ApWifiMac", "Ssid", ns.wifi.SsidValue (ssid), "BeaconGeneration", ns.core.BooleanValue (True))
	apDeviceC = wifi.Install (phy, mac, wifiApNode.Get(2))
	  
	# Network D

	ssid = ns.wifi.Ssid ("network-D")

	phy.Set ("ChannelNumber", ns.core.UintegerValue(48))
	mac.SetType ("ns3::StaWifiMac", "Ssid", ns.wifi.SsidValue (ssid), "BE_MaxAmpduSize", ns.core.UintegerValue (32768),"BE_MaxAmsduSize", ns.core.UintegerValue (3839))
	staDeviceD = wifi.Install (phy, mac, wifiStaNode.Get(3))
	mac.SetType ("ns3::ApWifiMac", "Ssid", ns.wifi.SsidValue (ssid), "BeaconGeneration", ns.core.BooleanValue (True))
	apDeviceD = wifi.Install (phy, mac, wifiApNode.Get(3))

	#  /* Setting mobility model */

	mobility = ns.mobility.MobilityHelper ()
	positionAlloc = ns.mobility.ListPositionAllocator ()
	mobility.SetMobilityModel ("ns3::ConstantPositionMobilityModel")

	#  //Set position for APs
	positionAlloc.Add (ns.core.Vector3D (0.0, 0.0, 0.0))
	positionAlloc.Add (ns.core.Vector3D (10.0, 0.0, 0.0))
	positionAlloc.Add (ns.core.Vector3D (20.0, 0.0, 0.0))
	positionAlloc.Add (ns.core.Vector3D (30.0, 0.0, 0.0))
	 
	# //Set position for STAs

	positionAlloc.Add (ns.core.Vector3D (distance, 0.0, 0.0))
	positionAlloc.Add (ns.core.Vector3D (10+distance, 0.0, 0.0))
	positionAlloc.Add (ns.core.Vector3D (20+distance, 0.0, 0.0))
	positionAlloc.Add (ns.core.Vector3D (30+distance, 0.0, 0.0))
	#  //Remark: while we set these positions 10 meters apart, the networks do not interact
	# //and the only variable that affects transmission performance is the distance.
	  

	mobility.SetPositionAllocator (positionAlloc)
	mobility.Install (wifiApNode)
	mobility.Install (wifiStaNode)


	# Internet stack
	stack = ns.internet.InternetStackHelper ()
	stack.Install (wifiApNode)
	stack.Install (wifiStaNode)

	address = ns.internet.Ipv4AddressHelper ()

	address.SetBase (ns.network.Ipv4Address ("192.168.1.0"), ns.network.Ipv4Mask ("255.255.255.0"))
	staInterfaceA = address.Assign (staDeviceA)
	apInterfaceA = address.Assign (apDeviceA)
	  
	address.SetBase (ns.network.Ipv4Address ("192.168.2.0"), ns.network.Ipv4Mask ("255.255.255.0"))
	staInterfaceB = address.Assign (staDeviceB)
	apInterfaceB = address.Assign (apDeviceB)

	address.SetBase (ns.network.Ipv4Address ("192.168.3.0"), ns.network.Ipv4Mask ("255.255.255.0"))
	staInterfaceC = address.Assign (staDeviceC)
	apInterfaceC = address.Assign (apDeviceC)

	address.SetBase (ns.network.Ipv4Address ("192.168.4.0"), ns.network.Ipv4Mask ("255.255.255.0"))
	staInterfaceD = address.Assign (staDeviceD)
	apInterfaceD = address.Assign (apDeviceD)

	#  /* Setting applications */

	serverAppA = ns.network.ApplicationContainer ()
	myServerA=ns.applications.UdpServerHelper (9)
	serverAppA = myServerA.Install (ns.network.NodeContainer (wifiStaNode.Get (0)))
	serverAppA.Start (ns.core.Seconds (0.0))
	serverAppA.Stop (ns.core.Seconds (simulationTime + 1))

	myClientA = ns.applications.UdpClientHelper (staInterfaceA.GetAddress (0), 9)
	myClientA.SetAttribute ("MaxPackets", ns.core.UintegerValue (4294967295))
	myClientA.SetAttribute ("Interval", ns.core.TimeValue (ns.core.Time ("0.00002"))) # packets/s
	myClientA.SetAttribute ("PacketSize", ns.core.UintegerValue (payloadSize))

	clientAppA = myClientA.Install (ns.network.NodeContainer (wifiApNode.Get (0)))
	clientAppA.Start (ns.core.Seconds (1.0))
	clientAppA.Stop (ns.core.Seconds (simulationTime + 1))
	  
	serverAppB = ns.network.ApplicationContainer ()
	myServerB=ns.applications.UdpServerHelper (9)
	serverAppB = myServerB.Install (ns.network.NodeContainer (wifiStaNode.Get (1)))
	serverAppB.Start (ns.core.Seconds (0.0))
	serverAppB.Stop (ns.core.Seconds (simulationTime + 1))

	myClientB = ns.applications.UdpClientHelper (staInterfaceB.GetAddress (0), 9)
	myClientB.SetAttribute ("MaxPackets", ns.core.UintegerValue (4294967295))
	myClientB.SetAttribute ("Interval", ns.core.TimeValue (ns.core.Time ("0.00002"))) # packets/s
	myClientB.SetAttribute ("PacketSize", ns.core.UintegerValue (payloadSize))

	clientAppB = myClientB.Install (ns.network.NodeContainer (wifiApNode.Get (1)))
	clientAppB.Start (ns.core.Seconds (1.0))
	clientAppB.Stop (ns.core.Seconds (simulationTime + 1))

	myClientC = ns.applications.UdpClientHelper (staInterfaceC.GetAddress (0), 9)
	myClientC.SetAttribute ("MaxPackets", ns.core.UintegerValue (4294967295))
	myClientC.SetAttribute ("Interval", ns.core.TimeValue (ns.core.Time ("0.00002"))) # packets/s
	myClientC.SetAttribute ("PacketSize", ns.core.UintegerValue (payloadSize))

	clientAppC = myClientC.Install (ns.network.NodeContainer (wifiApNode.Get (2)))
	clientAppC.Start (ns.core.Seconds (1.0))
	clientAppC.Stop (ns.core.Seconds (simulationTime + 1))

	myClientD = ns.applications.UdpClientHelper (staInterfaceD.GetAddress (0), 9)
	myClientD.SetAttribute ("MaxPackets", ns.core.UintegerValue (4294967295))
	myClientD.SetAttribute ("Interval", ns.core.TimeValue (ns.core.Time ("0.00002"))) # packets/s
	myClientD.SetAttribute ("PacketSize", ns.core.UintegerValue (payloadSize))

	clientAppD = myClientD.Install (ns.network.NodeContainer (wifiApNode.Get (3)))
	clientAppD.Start (ns.core.Seconds (1.0))
	clientAppD.Stop (ns.core.Seconds (simulationTime + 1))
  
	if (enablePcap):
		phy.EnablePcap ("AP_A-py", apDeviceA.Get (0))
		phy.EnablePcap ("STA_A-py", staDeviceA.Get (0))
		phy.EnablePcap ("AP_B-py", apDeviceB.Get (0))
		phy.EnablePcap ("STA_B-py", staDeviceB.Get (0))
		phy.EnablePcap ("AP_C-py", apDeviceC.Get (0))
		phy.EnablePcap ("STA_C-py", staDeviceC.Get (0))
		phy.EnablePcap ("AP_D-py", apDeviceD.Get (0))
		phy.EnablePcap ("STA_D-py", staDeviceD.Get (0))

	ns.core.Simulator.Stop (ns.core.Seconds (simulationTime + 1))
	ns.core.Simulator.Run ()
	ns.core.Simulator.Destroy ()

	totalPacketsThrough = serverAppA.Get (0).GetReceived ()
	throughput = totalPacketsThrough * payloadSize * 8 / (simulationTime * 1000000.0)
	print "Throughput with default configuration (A-MPDU aggregation enabled, 65kB): ", throughput,"Mbit/s\n"

	totalPacketsThrough = serverAppB.Get (0).GetReceived ()
	throughput = totalPacketsThrough * payloadSize * 8 / (simulationTime * 1000000.0)
	print "Throughput with aggregation disabled: ", throughput,"Mbit/s\n"

	totalPacketsThrough = serverAppC.Get (0).GetReceived ()
	throughput = totalPacketsThrough * payloadSize * 8 / (simulationTime * 1000000.0)
	print "Throughput with A-MPDU disabled and A-MSDU enabled (8kB): ", throughput,"Mbit/s\n"

	totalPacketsThrough = serverAppD.Get (0).GetReceived ()
	throughput = totalPacketsThrough * payloadSize * 8 / (simulationTime * 1000000.0)
	print "Throughput with A-MPDU enabled (32kB) and A-MSDU enabled (4kB): ", throughput,"Mbit/s\n"
	
	return 0

if __name__ == '__main__':
    import sys
sys.exit (main (sys.argv))

