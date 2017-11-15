import ns.applications
import ns.core
import ns.internet
import ns.network
import ns.point_to_point
import ns.csma
import ns.internet_apps


c = ns.network.NodeContainer()
c.Create(4)


csma = ns.csma.CsmaHelper()
csma.SetChannelAttribute("DataRate", ns.core.StringValue("100Mbps"))
csma.SetChannelAttribute("Delay", ns.core.TimeValue(ns.core.NanoSeconds(6560)))

csma.SetDeviceAttribute ("EncapsulationMode", ns.core.StringValue ("Llc"));
devs = csma.Install (c);

stack = ns.internet.InternetStackHelper()
stack.Install(c)


ip = ns.internet.Ipv4AddressHelper()
ip.SetBase(ns.network.Ipv4Address("10.1.1.0"),
                ns.network.Ipv4Mask("255.255.255.0"))
addresses = ns.internet.Ipv4InterfaceContainer()

addresses = ip.Assign(devs)


ns.core.Config.SetDefault ("ns3::Ipv4RawSocketImpl::Protocol", ns.core.StringValue ("2"))

dst = ns.network.InetSocketAddress (addresses.GetAddress (3))
onoff =ns.applications.OnOffHelper ("ns3::Ipv4RawSocketFactory", dst);
onoff.SetAttribute ("DataRate", ns.core.StringValue("15000"));
onoff.SetAttribute ("PacketSize", ns.core.UintegerValue (1200));

apps=ns.network.ApplicationContainer ()
apps = onoff.Install (c.Get (0));
apps.Start (ns.core.Seconds (1.0));
apps.Stop (ns.core.Seconds (10.0));

sink = ns.applications.PacketSinkHelper ("ns3::Ipv4RawSocketFactory", dst)
apps = sink.Install (c.Get (3));
apps.Start (ns.core.Seconds (0.0));
apps.Stop (ns.core.Seconds (11.0));

ping =ns.internet_apps.V4PingHelper(addresses.GetAddress(2));
pingers = ns.network.NodeContainer()
pingers.Add (c.Get (0));
pingers.Add (c.Get (1));
pingers.Add (c.Get (3));
apps = ping.Install (pingers);
apps.Start (ns.core.Seconds (2.0));
apps.Stop (ns.core.Seconds (5.0));


csma.EnablePcapAll("csma-ping", False)

ns.core.Simulator.Run()
ns.core.Simulator.Destroy()


