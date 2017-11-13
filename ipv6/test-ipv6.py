# /* -*-  Mode: C++; c-file-style: "gnu"; indent-tabs-mode:nil; -*- */
# /*
#  * Copyright (c) 2008 Louis Pasteur University / Telecom Bretagne
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
#  * Author: Angelos Chatzipapas <Angelos.CHATZIPAPAS@enst-bretagne.fr> /
#  * <chatzipa@ceid.upatras.gr>
#  */

import ns.network
import ns.core
import ns.applications

ns.core.LogComponentEnable("UdpEchoClientApplication", ns.core.LOG_LEVEL_ALL)

print "Test Ipv6"

m_addresses = [ None for _i in range(10) ] 

m_addresses[0] = ns.network.Mac48Address("00:00:00:00:00:01");
m_addresses[1] = ns.network.Mac48Address("00:00:00:00:00:02");
m_addresses[2] = ns.network.Mac48Address("00:00:00:00:00:03");
m_addresses[3] = ns.network.Mac48Address("00:00:00:00:00:04");
m_addresses[4] = ns.network.Mac48Address("00:00:00:00:00:05");
m_addresses[5] = ns.network.Mac48Address("00:00:00:00:00:06");
m_addresses[6] = ns.network.Mac48Address("00:00:00:00:00:07");
m_addresses[7] = ns.network.Mac48Address("00:00:00:00:00:08");
m_addresses[8] = ns.network.Mac48Address("00:00:00:00:00:09");
m_addresses[9] = ns.network.Mac48Address("00:00:00:00:00:10");

prefix1 = ns.network.Ipv6Address("2001:1::")

print "prefix = {0}".format(prefix1)

for i in range(10):
    print "address = {0}".format (m_addresses[i])
    ipv6address = ns.network.Ipv6Address.MakeAutoconfiguredAddress (m_addresses[i], prefix1)
    print "address = {0}".format (ipv6address)

prefix2 = ns.network.Ipv6Address("2002:1::")

print "prefix = {0}".format(prefix2)

for i in range(10):
    ipv6address = ns.network.Ipv6Address.MakeAutoconfiguredAddress (m_addresses[i], prefix2)
    print "address = {0}".format (ipv6address)
