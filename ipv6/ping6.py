import ns.applications
import ns.core
import ns.internet
import ns.network
import ns.point_to_point
import ns.mobility
import ns.wifi
import ns.csma
import ns.olsr

verbose = false
if (verbose)
    {
      ns.core.LogComponentEnable ("Ping6Example", ns.core.LOG_LEVEL_INFO);
      ns.core.LogComponentEnable ("Ipv6EndPointDemux", ns.core.LOG_LEVEL_ALL);
      ns.core.LogComponentEnable ("Ipv6L3Protocol", ns.core.LOG_LEVEL_ALL);
      ns.core.LogComponentEnable ("Ipv6StaticRouting", ns.core.LOG_LEVEL_ALL);
      ns.core.LogComponentEnable ("Ipv6ListRouting", ns.core.LOG_LEVEL_ALL);
      ns.core.LogComponentEnable ("Ipv6Interface", ns.core.LOG_LEVEL_ALL);
      ns.coreLogComponentEnable ("Icmpv6L4Protocol", ns.core.LOG_LEVEL_ALL);
      ns.core.LogComponentEnable ("Ping6Application", ns.core.LOG_LEVEL_ALL);
      ns.core.LogComponentEnable ("NdiscCache", ns.core.LOG_LEVEL_ALL);
    }

    print ("Create nodes.")
    n = ns.network.NodeContainer()
    n.Create(4)

    stack = ns.internet.InternetStackHelper()
    stack.Install(n)
    
    print ("Create channels.")
    csma=ns.csma.CsmaHelper()
    csma.SetChannelAttribute("DataRate", ns.network.DataRateValue(ns.network.DataRate(5000000)))
    csma.SetChannelAttribute("Delay", ns.core.TimeValue(ns.core.MilliSeconds(2)))
    d = csma.Install(n)

    print ("Assign IPv6 addresses")
    ipv6 = ns.internet.Ipv6AddressHelper()
    i = ipv6.assign(d)

    print ("Create applications")
    packetsize = 1024
    maxPacketCount = 5
    interPacketInterval = ns.core.Seconds(1.)
    ping6 = ns.applications.Ping6Helper()

    //one line here
    ping6.SetRemote(i.GetAddress(1, 1))

    ping6.SetAttribute("MaxPackets", ns.core.UintegerValue(maxPacketCount))
    ping6.SetAttribute("Interval", ns.core.TimeValue(interPacketInterval))
    ping6.SetAttribute("PacketSize", ns.core.UintegerValue(packetSize))
    apps = ping6.Install(ns.network.NodeContainer(n.Get(0)))
    apps.Start(ns.core.Seconds(2.0))
    apps.Stop(ns.core.Seconds(10.0))

    ascii = ns.network.AsciiTraceHelper()
    csma.EnableAsciiAll(ascii.CreateFileStream("ping6.tr"))
    csma.EnablePcapAll("ping6", True)
    
    print ("Run simulation")
    ns.core.Simulator.Run()
    ns.core.Simulator.Destroy()
