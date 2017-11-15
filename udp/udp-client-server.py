import ns.core
import ns.applications
import ns.internet
import ns.csma

def main(argv):
	ns.core.LogComponentEnable("UdpClient", ns.core.LOG_LEVEL_INFO)
	ns.core.LogComponentEnable("UdpServer", ns.core.LOG_LEVEL_INFO)
	cmd = ns.core.CommandLine ()
	cmd.useIpv6 = "False"
	cmd.AddValue ("useIpv6", "Use Ipv6")
	cmd.Parse (argv)
	
	print "Create nodes."
	n = ns.network.NodeContainer ()
	n.Create (2)
	
	internet = ns.internet.InternetStackHelper ()
	internet.Install (n)

	print "Create channels."
	csma = ns.csma.CsmaHelper ()
	csma.SetChannelAttribute ("DataRate", ns.core.StringValue ("5000000"))
	csma.SetChannelAttribute ("Delay", ns.core.TimeValue (ns.core.MilliSeconds (2)))
	csma.SetDeviceAttribute ("Mtu", ns.core.UintegerValue (1400))
	d = csma.Install (n)

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


	port = 4000  
	server = ns.applications.UdpEchoServerHelper (port)
	serverapps = server.Install (n.Get (1))
	serverapps.Start (ns.core.Seconds (1.0))
	serverapps.Stop (ns.core.Seconds (10.0))

	MaxPacketSize = 1024;
	interPacketInterval = ns.core.Seconds (0.05)
	maxPacketCount = 320;

	client = ns.applications.UdpEchoClientHelper ( serverAddress, port)


	client.SetAttribute ("MaxPackets", ns.core.UintegerValue (maxPacketCount))
  	client.SetAttribute ("Interval", ns.core.TimeValue (interPacketInterval))
 	client.SetAttribute ("PacketSize", ns.core.UintegerValue (MaxPacketSize))
  
	clientapps = client.Install (n.Get (0))
	serverapps.Start (ns.core.Seconds (2.0))
	serverapps.Stop (ns.core.Seconds (10.0))



	ascii = ns.network.AsciiTraceHelper ()
	csma.EnableAsciiAll (ascii.CreateFileStream ("udp-client-serv.tr"))
	csma.EnablePcapAll ("udp-client-serv", False)
	print "Run Simulation."
	ns.core.Simulator.Run ()
	ns.core.Simulator.Destroy ()
	print "Done."

if __name__ == '__main__':
    import sys
main (sys.argv)

 


















 




 






 






  

 
  
