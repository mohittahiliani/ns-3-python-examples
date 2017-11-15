# -*-  Mode: Python; -*-


import ns.core
import ns.csma
import ns.applications
import ns.internet

def main(argv):
	#
	# Users may find it convenient to turn on explicit debugging
	# for selected modules; the below lines suggest how to do this
	#
	ns.core.LogComponentEnable("UdpTraceClient", ns.core.LOG_LEVEL_INFO)
	ns.core.LogComponentEnable("UdpServer", ns.core.LOG_LEVEL_INFO)

	#
	# Allow the user to override any of the defaults at
	# run-time, via command-line arguments
	#
	cmd = ns.core.CommandLine ()
	cmd.useIpv6 = "False"
	cmd.AddValue ("useIpv6", "Use Ipv6")
	cmd.Parse (argv)
	
	 
	
	
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

	print "Create Applications."
	# 
	
	#
	port = 4000  # well-known echo port number
	server = ns.applications.UdpEchoServerHelper (port)
	serverapps = server.Install (n.Get (1))
	serverapps.Start (ns.core.Seconds (1.0))
	serverapps.Stop (ns.core.Seconds (10.0))
	
	
	
	MaxPacketSize = 1472
	client = ns.applications.UdpTraceClientHelper (serverAddress, port, "")
       # client= ns.applications.UdpTraceClientHelper(serverAddress,port,"")
        client.SetAttribute ("MaxPacketSize", ns.core.UintegerValue (MaxPacketSize))
	
	apps = client.Install (n)
	apps.Start (ns.core.Seconds (2.0))
	apps.Stop (ns.core.Seconds (10.0))
	
	

	asciitracer = ns.network.AsciiTraceHelper ()
	csma.EnableAsciiAll (asciitracer.CreateFileStream ("udp-trace.tr"))
	csma.EnablePcapAll ("udp-trace", False)
	
	# 
	# Now, do the actual simulation.
	# 
	print "Run Simulation."
	ns.core.Simulator.Run ()
	ns.core.Simulator.Destroy ()
	print "Done."

if __name__ == '__main__':
    import sys
main (sys.argv)
