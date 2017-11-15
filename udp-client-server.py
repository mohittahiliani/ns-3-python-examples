import ns.core
import ns.csma
import ns.internet
import ns.applications


def main(argv):
	cmd = ns.core.CommandLine ()
	cmd.useIpv6 = "False"
	cmd.AddValue ("useIpv6", "Use Ipv6")
	cmd.Parse (argv)

	# 
	# Explicitly create the nodes required by the topology (shown above).
	# 
	print "Create nodes."
	n = ns.network.NodeContainer ()
	n.Create (2)
	
	internetstack = ns.internet.InternetStackHelper ()
	internetstack.Install (n)

	# 
	# Explicitly create the channels required by the topology (shown above).
	# 
	print "Create channels."
	csma = ns.csma.CsmaHelper ()
	csma.SetChannelAttribute ("DataRate", ns.core.StringValue ("5000000"))
	csma.SetChannelAttribute ("Delay", ns.core.TimeValue (ns.core.MilliSeconds (2)))
	csma.SetDeviceAttribute ("Mtu", ns.core.UintegerValue (1400))
	d = csma.Install (n)

	# 
	# We've got the "hardware" in place.  Now we need to add IP addresses.
	# 
	print "Assign IP Addresses."
	if (cmd.useIpv6 == "False"):
		ipv4 = ns.internet.Ipv4AddressHelper ()
		ipv4.SetBase (ns.network.Ipv4Address ("10.1.1.0"), ns.network.Ipv4Mask ("255.255.255.0"))
		i = ipv4.Assign (d)
		serverAddress = ns.network.Address (i.GetAddress (1))
	    
	else:
		ipv6 = ns.internet.Ipv6AddressHelper ()
		ipv6.SetBase (ns.network.Ipv6Address ("2001:0000:f00d:cafe::"), ns.network.Ipv6Prefix (64))
		i6 = ipv6.Assign (d)
		serverAddress = ns.network.Address (i6.GetAddress (1, 1))

	#
	# Create one udpServer applications on node one.
	#	
	port = 4000;
	server = ns.applications.UdpServerHelper (port);
 	apps = server.Install (n)
  	apps.Start (ns.core.Seconds (1.0))
  	apps.Stop (ns.core.Seconds (10.0))

	#
	# Create one UdpClient application to send UDP datagrams from node zero to node one.
	#
 	MaxPacketSize = 1024
  	interPacketInterval = ns.core.Seconds (0.05)
  	maxPacketCount = 320
  	client = ns.applications.UdpClientHelper (serverAddress, port)
  	client.SetAttribute ("MaxPackets", ns.core.UintegerValue (maxPacketCount))
  	client.SetAttribute ("Interval", ns.core.TimeValue (interPacketInterval))
  	client.SetAttribute ("PacketSize", ns.core.UintegerValue (MaxPacketSize))
  	apps = client.Install (n)
  	apps.Start (ns.core.Seconds (2.0))
  	apps.Stop (ns.core.Seconds (10.0))

	asciitracer = ns.network.AsciiTraceHelper ()
	csma.EnableAsciiAll (asciitracer.CreateFileStream ("udp-client-server-py.tr"))
	csma.EnablePcapAll ("udp-client-server-py", False)

	print "Run Simulation."
	ns.core.Simulator.Run ()
	ns.core.Simulator.Destroy ()
	print "Done."

if __name__ == '__main__':
    import sys
    main (sys.argv)




