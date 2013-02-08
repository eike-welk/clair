# -*- coding: utf-8 -*-
###############################################################################
#    Clair - Project to discover prices on e-commerce sites.                  #
#                                                                             #
#    Copyright (C) 2013 by Eike Welk                                          #
#    eike.welk@gmx.net                                                        #
#                                                                             #
#    License: GPL                                                             #
#                                                                             #
#    This program is free software: you can redistribute it and/or modify     #
#    it under the terms of the GNU General Public License as published by     #
#    the Free Software Foundation, either version 3 of the License, or        #
#    (at your option) any later version.                                      #
#                                                                             #
#    This program is distributed in the hope that it will be useful,          #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of           #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            #
#    GNU General Public License for more details.                             #
#                                                                             #
#    You should have received a copy of the GNU General Public License        #
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.    #
###############################################################################
"""
Put module description here.
"""

from __future__ import division
from __future__ import absolute_import              

#import pytest #contains `skip`, `fail`, `raises`, `config`

from os.path import join, dirname, abspath
from datetime import datetime, timedelta
from lxml import etree
import pandas as pd



def relative(*paths):
    "Create file paths that are relative to the location of this file."
    return abspath(join(dirname(abspath(__file__)), *paths))

def test_convert_ebay_condition():
    """
    Test conversion Ebay condition numbers to internal condition numbers.
    
    http://developer.ebay.com/DevZone/finding/CallRef/Enums/conditionIdList.html

    --------------------------------------------------------------
    Ebay     Description                    Internal number
    ----     ---------------------------    ----------------------
    1000     New, brand-new                 1.0
    3000     Used
    7000     For parts or not working       0.1
    --------------------------------------------------------------
    """
    from clair.network import convert_ebay_condition
    
    print convert_ebay_condition(1000)
    assert abs(convert_ebay_condition(1000) - 1.0) < 0.0001

    print convert_ebay_condition(7000)
    assert abs(convert_ebay_condition(7000) - 0.1) < 0.0001

    print convert_ebay_condition(3000)
    
    
#---- EbayFindListings --------------------------------------------------------    

#A successful response from Ebay for findItemsByKeywords
EBAY_findItemsByKeywords_RESPONSE = \
"""
<findItemsByKeywordsResponse xmlns="http://www.ebay.com/marketplace/search/v1/services">
  <ack>Success</ack>
  <version>1.12.0</version>
  <timestamp>2013-02-05T03:25:44.137Z</timestamp>
  <searchResult count="2">
    <item>
      <itemId>370730491804</itemId>
      <title>Ipod Clock Radio Dock Bad Boy Black AC NEU</title>
      <globalId>EBAY-DE</globalId>
      <primaryCategory>
        <categoryId>171949</categoryId>
        <categoryName>Sonstige</categoryName>
      </primaryCategory>
      <galleryURL>http://thumbs1.ebaystatic.com/m/mDVUZpivkdfPdyKHCY2vlxA/140.jpg</galleryURL>
      <viewItemURL>http://www.ebay.de/itm/Ipod-Clock-Radio-Dock-Bad-Boy-Black-AC-NEU-/370730491804?pt=LH_DefaultDomain_77</viewItemURL>
      <paymentMethod>CIPInCheckoutEnabled</paymentMethod>
      <paymentMethod>PayPal</paymentMethod>
      <paymentMethod>MoneyXferAccepted</paymentMethod>
      <autoPay>false</autoPay>
      <location>Gro&#223;britannien</location>
      <country>GB</country>
      <shippingInfo>
        <shippingServiceCost currencyId="EUR">0.0</shippingServiceCost>
        <shippingType>Free</shippingType>
        <shipToLocations>Worldwide</shipToLocations>
      </shippingInfo>
      <sellingStatus>
        <currentPrice currencyId="EUR">55.54</currentPrice>
        <convertedCurrentPrice currencyId="EUR">55.54</convertedCurrentPrice>
        <sellingState>Active</sellingState>
        <timeLeft>P0DT1H4M18S</timeLeft>
      </sellingStatus>
      <listingInfo>
        <bestOfferEnabled>false</bestOfferEnabled>
        <buyItNowAvailable>false</buyItNowAvailable>
        <startTime>2013-01-06T04:25:02.000Z</startTime>
        <endTime>2013-02-05T04:30:02.000Z</endTime>
        <listingType>StoreInventory</listingType>
        <gift>false</gift>
      </listingInfo>
      <condition>
        <conditionId>1000</conditionId>
        <conditionDisplayName>Neu</conditionDisplayName>
      </condition>
      <isMultiVariationListing>false</isMultiVariationListing>
      <topRatedListing>false</topRatedListing>
    </item>
    <item>
      <itemId>261163201066</itemId>
      <title>Apple iPod nano 5. Generation Orange (8 GB)</title>
      <globalId>EBAY-DE</globalId>
      <primaryCategory>
        <categoryId>73839</categoryId>
        <categoryName>iPods &amp; MP3-Player</categoryName>
      </primaryCategory>
      <galleryURL>http://thumbs3.ebaystatic.com/m/maHJnxEF0YFQ1CDq_mZhpqw/140.jpg</galleryURL>
      <viewItemURL>http://www.ebay.de/itm/Apple-iPod-nano-5-Generation-Orange-8-GB-/261163201066?pt=DE_MP3_Players</viewItemURL>
      <productId type="ReferenceID">77793916</productId>
      <paymentMethod>CIPInCheckoutEnabled</paymentMethod>
      <paymentMethod>PayPal</paymentMethod>
      <paymentMethod>MoneyXferAccepted</paymentMethod>
      <autoPay>false</autoPay>
      <postalCode>04774</postalCode>
      <location>Dahlen,Deutschland</location>
      <country>DE</country>
      <shippingInfo>
        <shippingServiceCost currencyId="EUR">5.0</shippingServiceCost>
        <shippingType>Flat</shippingType>
        <shipToLocations>DE</shipToLocations>
      </shippingInfo>
      <sellingStatus>
        <currentPrice currencyId="EUR">70.5</currentPrice>
        <convertedCurrentPrice currencyId="EUR">70.5</convertedCurrentPrice>
        <bidCount>17</bidCount>
        <sellingState>Active</sellingState>
        <timeLeft>P0DT1H31M56S</timeLeft>
      </sellingStatus>
      <listingInfo>
        <bestOfferEnabled>false</bestOfferEnabled>
        <buyItNowAvailable>false</buyItNowAvailable>
        <startTime>2013-01-31T04:57:40.000Z</startTime>
        <endTime>2013-02-05T04:57:40.000Z</endTime>
        <listingType>Auction</listingType>
        <gift>false</gift>
      </listingInfo>
      <condition>
        <conditionId>3000</conditionId>
        <conditionDisplayName>Gebraucht</conditionDisplayName>
      </condition>
      <isMultiVariationListing>false</isMultiVariationListing>
      <topRatedListing>false</topRatedListing>
    </item>
  </searchResult>
  <paginationOutput>
    <totalPages>225</totalPages>
    <totalEntries>449</totalEntries>
    <pageNumber>1</pageNumber>
    <entriesPerPage>2</entriesPerPage>
  </paginationOutput>
  <itemSearchURL>http://www.ebay.de/sch/i.html?endtimefrom=2013-02-05T03%3A35%3A43.000Z&amp;_nkw=ipod&amp;endtimeto=2013-02-07T03%3A25%3A43.000Z&amp;_LH_Time=1&amp;_ddo=1&amp;_ett=47.99971027777778&amp;_ftrt=902&amp;_ftrv=0.16637694444444445&amp;_ipg=2&amp;_mPrRngCbx=1&amp;_pgn=1&amp;_sop=1&amp;_udhi=73%2C01&amp;_udlo=36%2C51</itemSearchURL>
</findItemsByKeywordsResponse>
"""


def test_EbayFindListings_download():
    """Test access to Ebay site and download_xml of XML."""
    from clair.network import EbayFindListings
    from ebay.utils import set_config_file
    
    set_config_file(relative("../python-ebay.apikey"))
    
    f = EbayFindListings()
    xml = f.download_xml(keywords="ipod", 
                         entries_per_page=2, 
                         page_number=1, 
                         min_price=50, 
                         max_price=100, 
                         currency="EUR", 
                         time_from=datetime.utcnow() + timedelta(minutes=10), 
                         time_to=  datetime.utcnow() + timedelta(days=2))
#    print xml
    
    root = etree.fromstring(xml)
    print etree.tostring(root, pretty_print=True)
    ack = root.find("{http://www.ebay.com/marketplace/search/v1/services}ack").text
    assert ack == "Success"


def test_EbayFindListings_parse():
    """Test parsing of XML response."""
    from clair.network import EbayFindListings
    
    f = EbayFindListings()
    listings = f.parse_xml(EBAY_findItemsByKeywords_RESPONSE)
    
    print listings
    print
    print listings[["title", "price", "currency"]]
    
    #There are two listings (items) in the response
    assert len(listings) == 2


def test_EbayFindListings_find():
    """Test higher level interface to find listings on Ebay by keyword."""
    from clair.network import EbayFindListings
    from ebay.utils import set_config_file
    
    set_config_file(relative("../python-ebay.apikey"))
    
    f = EbayFindListings()
    
    listings = f.find(keywords="ipod", n_listings=5)
    print listings[["title", "price", "currency"]].to_string()
    print
    assert len(listings) == 5
    
    #Four calls necessary
    n = 305
    listings = f.find(keywords="ipod", n_listings=n)
    print listings
#    listings.to_csv("listings.csv", encoding="utf8")
    #Duplicates are removed, algorithm might return slightly more listings
    assert n * 0.8 <= len(listings) <= n + 1.01 
    
#---- EbayGetListings --------------------------------------------------------- 

EBAY_GetMultipleItemsResponse_RESPONSE = \
"""
  <GetMultipleItemsResponse xmlns="urn:ebay:apis:eBLBaseComponents">
   <Timestamp>2013-02-07T06:24:35.687Z</Timestamp>
   <Ack>Success</Ack>
   <Build>E809_CORE_BUNDLED_15734399_R1</Build>
   <Version>809</Version>
   <Item>
    <BestOfferEnabled>false</BestOfferEnabled>
    <Description>Nikon D90, Sehr guter Zustand bis auf die seitlich fehlende Gummi Abdeckung (siehe Bilder) Angebot beinhaltet: Nikon D90 Body, Tragegurt, Ladegerät, AV- und USB-Kabel. Aputure LCD Fernauslöser http://www.aputure.com/en/product/digital_timer_remote_shutter.php (original Verpackung) Seagull Winkelsucher http://www.camerachina.com/productxx.asp?id=1349 (original Verpackung) Lowepro Sling Shot 100 AW Tasche.</Description>
    <ItemID>221185477679</ItemID>
    <EndTime>2013-02-08T16:15:47.000Z</EndTime>
    <StartTime>2013-02-03T16:15:47.000Z</StartTime>
    <ViewItemURLForNaturalSearch>http://www.ebay.de/itm/Nikon-D90-18-55mm-3-5-5-6G-Objektiv-Zubehoerpaket-/221185477679</ViewItemURLForNaturalSearch>
    <ListingType>Chinese</ListingType>
    <Location>Würzburg</Location>
    <PaymentMethods>MoneyXferAccepted</PaymentMethods>
    <PaymentMethods>MoneyXferAcceptedInCheckout</PaymentMethods>
    <PaymentMethods>PaymentSeeDescription</PaymentMethods>
    <GalleryURL>http://thumbs4.ebaystatic.com/pict/2211854776798080_1.jpg</GalleryURL>
    <PictureURL>http://i.ebayimg.com/00/s/NzY4WDEwMjQ=/z/ubkAAOxyq5NRDoF9/$T2eC16dHJGoE9nuQg1kgBRDoF985ng~~60_1.JPG?set_id=8800005007</PictureURL>
    <PictureURL>http://i.ebayimg.com/00/s/NzY4WDEwMjQ=/z/Op4AAOxyhs9RDoF2/$(KGrHqVHJFYFD1i3iGR9BRDoF2goLw~~60_1.JPG?set_id=8800005007</PictureURL>
    <PictureURL>http://i.ebayimg.com/00/s/NzY4WDEwMjQ=/z/NVgAAOxyOBJRDoF8/$(KGrHqYOKocFDwEk(PU-BRDoF7zwn!~~60_1.JPG?set_id=8800005007</PictureURL>
    <PictureURL>http://i.ebayimg.com/00/s/NzY4WDEwMjQ=/z/L9kAAMXQNOZRDoF8/$(KGrHqRHJE0FD7-hl63LBRDoF8t4ow~~60_1.JPG?set_id=8800005007</PictureURL>
    <PictureURL>http://i.ebayimg.com/00/s/NzY4WDEwMjQ=/z/TNYAAMXQQUpRDoF9/$(KGrHqRHJEMFD1mW!-pWBRDoF8rJgg~~60_1.JPG?set_id=8800005007</PictureURL>
    <PictureURL>http://i.ebayimg.com/00/s/NzY4WDEwMjQ=/z/TNQAAMXQQUpRDoF9/$T2eC16hHJHgE9n0yHFDqBRDoF8r(Mw~~60_1.JPG?set_id=8800005007</PictureURL>
    <PictureURL>http://i.ebayimg.com/00/s/NzY4WDEwMjQ=/z/2-UAAMXQbXtRDoGA/$T2eC16RHJHEE9ny2q81kBRDoF+veI!~~60_1.JPG?set_id=8800005007</PictureURL>
    <PostalCode>97082</PostalCode>
    <PrimaryCategoryID>31388</PrimaryCategoryID>
    <PrimaryCategoryName>Foto &amp; Camcorder:Digitalkameras</PrimaryCategoryName>
    <Quantity>1</Quantity>
    <Seller>
     <UserID>carismadm</UserID>
     <FeedbackRatingStar>Blue</FeedbackRatingStar>
     <FeedbackScore>93</FeedbackScore>
     <PositiveFeedbackPercent>100.0</PositiveFeedbackPercent>
    </Seller>
    <BidCount>0</BidCount>
    <ConvertedCurrentPrice currencyID="EUR">320.0</ConvertedCurrentPrice>
    <CurrentPrice currencyID="EUR">320.0</CurrentPrice>
    <ListingStatus>Active</ListingStatus>
    <QuantitySold>0</QuantitySold>
    <ShipToLocations>DE</ShipToLocations>
    <Site>Germany</Site>
    <TimeLeft>P1DT9H51M12S</TimeLeft>
    <Title>Nikon D90  mit 18-55mm 3.5-5.6G Objektiv + Zubehörpaket</Title>
    <ShippingCostSummary>
     <ShippingServiceCost currencyID="EUR">6.9</ShippingServiceCost>
     <ShippingType>Flat</ShippingType>
     <ListedShippingServiceCost currencyID="EUR">6.9</ListedShippingServiceCost>
    </ShippingCostSummary>
    <ItemSpecifics>
     <NameValueList>
      <Name>Marke</Name>
      <Value>Nikon</Value>
     </NameValueList>
     <NameValueList>
      <Name>Modell</Name>
      <Value>D90</Value>
     </NameValueList>
     <NameValueList>
      <Name>Produktart</Name>
      <Value>DSLR-Kamera</Value>
     </NameValueList>
     <NameValueList>
      <Name>Farbe</Name>
      <Value>Schwarz</Value>
     </NameValueList>
     <NameValueList>
      <Name>Optischer Zoom</Name>
      <Value>3x</Value>
     </NameValueList>
     <NameValueList>
      <Name>Megapixel</Name>
      <Value>12.3 MP</Value>
     </NameValueList>
     <NameValueList>
      <Name>Bildschirmgröße</Name>
      <Value>7,62 cm (3 Zoll)</Value>
     </NameValueList>
     <NameValueList>
      <Name>MPN</Name>
      <Value>VBA230KG16</Value>
     </NameValueList>
    </ItemSpecifics>
    <HitCount>137</HitCount>
    <PrimaryCategoryIDPath>625:31388</PrimaryCategoryIDPath>
    <Country>DE</Country>
    <ReturnPolicy>
     <ReturnsAccepted>ReturnsNotAccepted</ReturnsAccepted>
    </ReturnPolicy>
    <MinimumToBid currencyID="EUR">320.0</MinimumToBid>
    <ProductID type="Reference">100128074</ProductID>
    <AutoPay>false</AutoPay>
    <IntegratedMerchantCreditCardEnabled>false</IntegratedMerchantCreditCardEnabled>
    <HandlingTime>3</HandlingTime>
    <ConditionID>3000</ConditionID>
    <ConditionDisplayName>Gebraucht</ConditionDisplayName>
    <GlobalShipping>false</GlobalShipping>
   </Item>
   <Item>
    <BestOfferEnabled>false</BestOfferEnabled>
    <Description>Wegen Systemwechsels verkaufe ich meine völlig intakte und wenig genutzte Nikon D90. Mit der Kamera wurden weniger als 4050 Bilder (laut robo47.net) gemacht. Die Kamera wird geliefert in der OVP mit allem Zubehör. Hinweis: Die OVP hat als Aufdruck das Kit mit einem (qualitativ nicht sehr hochwertigem Kit-Objektiv). Das habe ich allerdings nicht mit erworben und wird auch nicht mitgeliefert (der Fotoladen hatte nur noch das Kit und so wurde das Objektiv aus der Packung herausgenommen). Zusätzlich liefere ich noch - ein gesondertes Kamerahandbuch (Heike Jasper: Das Kamerahandbuch Nikon D90, Galileo Design Verlag, Neupreis 39,90 Euro). Dieses Handbuch ist viel hilfreicher als die Bedienungsanleitung des Herstellers.- eine kompakte Lowepro-Kameratasche, in die die D90 mit einem mittelgroßen Objektiv gut hineinpasst.</Description>
    <ItemID>271149493368</ItemID>
    <EndTime>2013-02-07T20:02:55.000Z</EndTime>
    <StartTime>2013-02-02T20:02:55.000Z</StartTime>
    <ViewItemURLForNaturalSearch>http://www.ebay.de/itm/Nikon-D90-Digitalkamera-OVP-/271149493368</ViewItemURLForNaturalSearch>
    <ListingType>Chinese</ListingType>
    <Location>Berlin</Location>
    <PaymentMethods>MoneyXferAccepted</PaymentMethods>
    <PaymentMethods>PayPal</PaymentMethods>
    <PaymentMethods>MoneyXferAcceptedInCheckout</PaymentMethods>
    <GalleryURL>http://thumbs1.ebaystatic.com/pict/2711494933688080_1.jpg</GalleryURL>
    <PictureURL>http://i.ebayimg.com/00/s/MTIwMFgxNjAw/$(KGrHqRHJFUFDydhmHV5BQ9wD3Rp0!~~60_1.JPG?set_id=8800005007</PictureURL>
    <PictureURL>http://i.ebayimg.com/00/s/MTIwMFgxNjAw/$T2eC16hHJFoE9nh6qSR5BQ9wEeD7Tw~~60_1.JPG?set_id=8800005007</PictureURL>
    <PictureURL>http://i.ebayimg.com/00/s/MTIwMFgxNjAw/$T2eC16NHJGwE9n)ySf0JBQ9wFGfv9Q~~60_1.JPG?set_id=8800005007</PictureURL>
    <PostalCode>10437</PostalCode>
    <PrimaryCategoryID>31388</PrimaryCategoryID>
    <PrimaryCategoryName>Foto &amp; Camcorder:Digitalkameras</PrimaryCategoryName>
    <Quantity>1</Quantity>
    <Seller>
     <UserID>realblaumann</UserID>
     <FeedbackRatingStar>Blue</FeedbackRatingStar>
     <FeedbackScore>82</FeedbackScore>
     <PositiveFeedbackPercent>100.0</PositiveFeedbackPercent>
    </Seller>
    <BidCount>8</BidCount>
    <ConvertedCurrentPrice currencyID="EUR">294.0</ConvertedCurrentPrice>
    <CurrentPrice currencyID="EUR">294.0</CurrentPrice>
    <HighBidder>
     <UserID>e***e</UserID>
     <FeedbackPrivate>false</FeedbackPrivate>
     <FeedbackRatingStar>Turquoise</FeedbackRatingStar>
     <FeedbackScore>203</FeedbackScore>
    </HighBidder>
    <ListingStatus>Active</ListingStatus>
    <QuantitySold>0</QuantitySold>
    <ShipToLocations>DE</ShipToLocations>
    <Site>Germany</Site>
    <TimeLeft>PT13H38M20S</TimeLeft>
    <Title>Nikon D90 Digitalkamera mit OVP </Title>
    <ShippingCostSummary>
     <ShippingServiceCost currencyID="EUR">7.0</ShippingServiceCost>
     <ShippingType>Flat</ShippingType>
     <ListedShippingServiceCost currencyID="EUR">7.0</ListedShippingServiceCost>
    </ShippingCostSummary>
    <ItemSpecifics>
     <NameValueList>
      <Name>Marke</Name>
      <Value>Nikon</Value>
     </NameValueList>
     <NameValueList>
      <Name>Modell</Name>
      <Value>D90</Value>
     </NameValueList>
     <NameValueList>
      <Name>Produktart</Name>
      <Value>DSLR-Kamera</Value>
     </NameValueList>
     <NameValueList>
      <Name>Farbe</Name>
      <Value>Schwarz</Value>
     </NameValueList>
     <NameValueList>
      <Name>Megapixel</Name>
      <Value>12.3 MP</Value>
     </NameValueList>
     <NameValueList>
      <Name>Bildschirmgröße</Name>
      <Value>7,62 cm (3 Zoll)</Value>
     </NameValueList>
     <NameValueList>
      <Name>MPN</Name>
      <Value>VBA230AE</Value>
     </NameValueList>
    </ItemSpecifics>
    <HitCount>247</HitCount>
    <Subtitle>Zusammen mit extra Kamerahandbuch und Lowepro-Tasche </Subtitle>
    <PrimaryCategoryIDPath>625:31388</PrimaryCategoryIDPath>
    <Country>DE</Country>
    <ReturnPolicy>
     <ReturnsAccepted>ReturnsNotAccepted</ReturnsAccepted>
    </ReturnPolicy>
    <MinimumToBid currencyID="EUR">295.0</MinimumToBid>
    <ProductID type="Reference">100172951</ProductID>
    <AutoPay>false</AutoPay>
    <IntegratedMerchantCreditCardEnabled>false</IntegratedMerchantCreditCardEnabled>
    <HandlingTime>3</HandlingTime>
    <ConditionID>3000</ConditionID>
    <ConditionDisplayName>Gebraucht</ConditionDisplayName>
    <GlobalShipping>false</GlobalShipping>
   </Item>
   <Item>
    <BestOfferEnabled>false</BestOfferEnabled>
    <Description>FLIP4SHOP Zu bevorzugten Shops hinzufügen Artikelbeschreibung Nikon D90 12,3MP mit Zubehör in OVP! Mit Rechnung vom Fachhändler und 1 Jahr Gewährleistung Die Nikon D90 bietet Filmsequenzfunktion (D-Movie) in HD-Auflösung. Der CMOS-Bildsensor im DX-Format mit einer effektiven Auflösung von 12,3 Megapixel und das Bildverarbeitungssystem EXPEED von Nikon sind Garanten für die erstklassige Bildqualität der D90. Weitere Funktionen wie Live-View, Motiverkennung, Aktives D-Lighting, Picture Control und hoher Empfindlichkeitsbereich. Details: Nikon D90 12,3MP Zustand: Sehr Gut Die Kamera funktioniert Technisch einwandfrei Das Gehäuse weist feinste Gebrauchsspuren auf. Es befindet sich in einem sehr guten Zustand Das Display weist wenige feinste Kratzer auf, diese sind bei der Benutzung nicht weiter störend Das Gerät stammt aus einem Raucherhaushalt Shutter Counts (Auslösungen) 3600 Highlights: CMOS-Bildsensor im DX-Format mit 12,3 Megapixel Auflösung und integriertem Sensorreinigungssystem, Kaum Bildrauschen von ISO 200 bis 3.200 Live-View mit hochauflösendem 7,6cm (3 Zoll) LCD-Monitor mit 920.000 Bildpunkten HD-Movie-Funktion zur Aufnahme von Motion-JPEG-Filmen mit der hervorragenden Bildqualität einer digitalen Spiegelreflexkamera Technische Daten: Auflösung: 12,3MPDisplaygröße/matt/glänzend?: 3&quot; TFT-LCD-Monitor mit 920.000 BildpunktenDigitalkameratyp: SpiegelreflexSpeichermedium: SD-KarteStromversorgung: Lithium-Ionen Lieferumfang: Nikon D90 12,3MP - schwarz Nikon Quick Charger MH-18a Ladegerät + Netzkabel Nikon Trageriemen Nikon BM-10 Displayschutz Nikon Gehäuseabdeckung USB,-AV,-Kabel Anleitung, Software CD und Originalverpackung Kein Objektiv und Li-ion Akku im Lieferumfang enthalten Kein weiteres Zubehör enthalten Gewährleistung und Rechnung: Rechnung vom Fachhändler FLIP4SHOP Die angegebenen Preise sind Endpreise zzgl. eventueller Versandkosten. Da es sich um differenzbesteuerte Waren (§ 25a UStG) handelt, ist die MwSt. im Preis zwar entsprechend der Regelungen zur Differenzbesteuerung enthalten, ein Umsatzsteuerausweis auf der Rechnung jedoch nicht möglich. 12 Monate Gewährleistung Shop-Kategorien Shop Startseite Apple iPods Apple Macs Apple Notebooks Digitalkameras Mobiltelefone Fragen zum Angebot? Sie erreichen unseren Kundenservice unter der folgenden Telefonnummer: Tel. 0180 5 354746* Fax. 06172-1794 201 E-Mail: info@flip4new.de *0,14 Euro pro Minute aus dem Festnetz; maximal 0,42 Euro pro Minute aus den Mobilfunknetzen Verpackung &amp; Versand Wir versenden unsere Geräte ausschließlich über unseren Partner DHL. Dies garantiert einen: sicheren günstigen schnellen Versandprozess. Falls Ihre Zahlung uns bis 13:00 Uhr erreicht, wird Ihr Gerät in der Regel noch am selben Tag versendet.</Description>
    <ItemID>140914051088</ItemID>
    <EndTime>2013-02-13T10:15:15.000Z</EndTime>
    <StartTime>2013-02-06T10:15:15.000Z</StartTime>
    <ViewItemURLForNaturalSearch>http://www.ebay.de/itm/Nikon-D90-12-3-MP-Digitalkamera-Schwarz-Nur-Gehaeuse-OVP-Fachhaendler-/140914051088</ViewItemURLForNaturalSearch>
    <ListingType>StoresFixedPrice</ListingType>
    <Location>Frankfurt</Location>
    <PaymentMethods>MoneyXferAccepted</PaymentMethods>
    <PaymentMethods>PayPal</PaymentMethods>
    <PaymentMethods>MoneyXferAcceptedInCheckout</PaymentMethods>
    <GalleryURL>http://thumbs1.ebaystatic.com/pict/1409140510888080_1.jpg</GalleryURL>
    <PictureURL>http://i.ebayimg.com/00/$(KGrHqV,!lkE4lTJtG2)BOPpl8sEZQ~~_8.JPG?set_id=89040003C1</PictureURL>
    <PostalCode>60489</PostalCode>
    <PrimaryCategoryID>31388</PrimaryCategoryID>
    <PrimaryCategoryName>Foto &amp; Camcorder:Digitalkameras</PrimaryCategoryName>
    <Quantity>1</Quantity>
    <Seller>
     <UserID>flip4shop</UserID>
     <FeedbackRatingStar>PurpleShooting</FeedbackRatingStar>
     <FeedbackScore>51297</FeedbackScore>
     <PositiveFeedbackPercent>99.7</PositiveFeedbackPercent>
     <TopRatedSeller>true</TopRatedSeller>
    </Seller>
    <BidCount>0</BidCount>
    <ConvertedCurrentPrice currencyID="EUR">359.29</ConvertedCurrentPrice>
    <CurrentPrice currencyID="EUR">359.29</CurrentPrice>
    <ListingStatus>Active</ListingStatus>
    <QuantitySold>0</QuantitySold>
    <ShipToLocations>Europe</ShipToLocations>
    <Site>Germany</Site>
    <TimeLeft>P6DT3H50M40S</TimeLeft>
    <Title>Nikon D90 12.3 MP Digitalkamera - Schwarz (Nur Gehäuse) in OVP - vom Fachhändler</Title>
    <ShippingCostSummary>
     <ShippingServiceCost currencyID="EUR">0.0</ShippingServiceCost>
     <ShippingType>Flat</ShippingType>
     <ListedShippingServiceCost currencyID="EUR">0.0</ListedShippingServiceCost>
    </ShippingCostSummary>
    <ItemSpecifics>
     <NameValueList>
      <Name>Marke</Name>
      <Value>Nikon</Value>
     </NameValueList>
     <NameValueList>
      <Name>Modell</Name>
      <Value>D90</Value>
     </NameValueList>
     <NameValueList>
      <Name>Produktart</Name>
      <Value>DSLR-Kamera</Value>
     </NameValueList>
     <NameValueList>
      <Name>Farbe</Name>
      <Value>Schwarz</Value>
     </NameValueList>
     <NameValueList>
      <Name>Megapixel</Name>
      <Value>12,3 MP</Value>
     </NameValueList>
     <NameValueList>
      <Name>Bildschirmgröße</Name>
      <Value>7,62 cm (3 Zoll)</Value>
     </NameValueList>
     <NameValueList>
      <Name>MPN</Name>
      <Value>VBA230AE</Value>
     </NameValueList>
    </ItemSpecifics>
    <HitCount>24</HitCount>
    <Subtitle>Mit Rechnung vom Fachhändler - 12 Monate Gewährleistung</Subtitle>
    <PrimaryCategoryIDPath>625:31388</PrimaryCategoryIDPath>
    <Storefront>
     <StoreURL>http://stores.ebay.de/id=986579248</StoreURL>
     <StoreName>FLIP4SHOP</StoreName>
    </Storefront>
    <Country>DE</Country>
    <ReturnPolicy>
     <ReturnsAccepted>Verbraucher haben das Recht, den Artikel unter den angegebenen Bedingungen zurückzugeben.</ReturnsAccepted>
     <Description>Widerrufsbelehrung&#xd;
&#xd;
&#xd;
Widerrufsrecht&#xd;
Sie können Ihre Vertragserklärung innerhalb von 14 Tagen ohne Angabe von Gründen in Textform (z. B. Brief, Fax, E-Mail) oder – wenn Ihnen die Sache vor Fristablauf überlassen wird – auch durch Rücksendung der Sache widerrufen. Die Frist beginnt nach Erhalt dieser Belehrung in Textform, jedoch nicht vor Eingang der Ware beim Empfänger (bei der wiederkehrenden Lieferung gleichartiger Waren nicht vor Eingang der ersten Teillieferung) und auch nicht vor Erfüllung unserer Informationspflichten gemäß Artikel 246 § 2 in Verbindung mit § 1 Absatz 1 und 2 EGBGB sowie unserer Pflichten gemäß § 312g Absatz 1 Satz 1 BGB in Verbindung mit Artikel 246 § 3 EGBGB. Zur Wahrung der Widerrufsfrist genügt die rechtzeitige Absendung des Widerrufs oder der Sache. &#xd;
&#xd;
Der Widerruf ist zu richten an:&#xd;
&#xd;
Flip4 GmbH &#xd;
Industriestrasse 21&#xd;
61381  Friedrichsdorf  Deutschland  &#xd;
 Fax: 06172 – 1794 201&#xd;
 E-Mail: info@flip4new.de&#xd;
&#xd;
Widerrufsfolgen &#xd;
Im Falle eines wirksamen Widerrufs sind die beiderseits empfangenen Leistungen zurückzugewähren und ggf. gezogene Nutzungen (z. B. Zinsen) herauszugeben. Können Sie uns die empfangene Leistung sowie Nutzungen (z.B. Gebrauchsvorteile) nicht oder teilweise nicht oder nur in verschlechtertem Zustand zurückgewähren beziehungsweise herausgeben, müssen Sie uns insoweit Wertersatz leisten. Für die Verschlechterung der Sache und für gezogene Nutzungen müssen Sie Wertersatz nur leisten, soweit die Nutzungen oder die Verschlechterung auf einen Umgang mit der Sache zurückzuführen ist, der über die Prüfung der Eigenschaften und der Funktionsweise hinausgeht. Unter „Prüfung der Eigenschaften und der Funktionsweise“ versteht man das Testen und Ausprobieren der jeweiligen Ware, wie es etwa im Ladengeschäft möglich und üblich ist.&#xd;
&#xd;
Paketversandfähige Sachen sind auf unsere Gefahr zurückzusenden. Sie haben die regelmäßigen Kosten der Rücksendung zu tragen, wenn die gelieferte Ware der bestellten entspricht und wenn der Preis der zurückzusendenden Sache einen Betrag von 40 Euro nicht übersteigt oder wenn Sie bei einem höheren Preis der Sache zum Zeitpunkt des Widerrufs noch nicht die Gegenleistung oder eine vertraglich vereinbarte Teilzahlung erbracht haben. Andernfalls ist die Rücksendung für Sie kostenfrei. Nicht paketversandfähige Sachen werden bei Ihnen abgeholt. Verpflichtungen zur Erstattung von Zahlungen müssen innerhalb von 30 Tagen erfüllt werden. Die Frist beginnt für Sie mit der Absendung Ihrer Widerrufserklärung oder der Sache, für uns mit deren Empfang.&#xd;
&#xd;
Beachten Sie: Das Widerrufsrecht besteht gem. § 312d BGB, soweit nicht ein anderes bestimmt ist, nicht bei Fernabsatzverträgen.&#xd;
&#xd;
1    zur Lieferung von Waren, die nach Kundenspezifikation angefertigt werden oder eindeutig auf die persönlichen Bedürfnisse zugeschnitten sind oder die auf Grund ihrer Beschaffenheit nicht für eine Rücksendung geeignet sind oder schnell verderben können oder deren Verfalldatum überschritten würde,&#xd;
&#xd;
2    zur Lieferung von Audio- oder Videoaufzeichnungen oder von Software, sofern die gelieferten Datenträger vom Verbraucher entsiegelt worden sind,&#xd;
&#xd;
3    zur Lieferung von Zeitungen, Zeitschriften und Illustrierten, es sei denn, dass der Verbraucher seine Vertragserklärung telefonisch abgegeben hat.</Description>
    </ReturnPolicy>
    <ProductID type="Reference">100172951</ProductID>
    <AutoPay>false</AutoPay>
    <BusinessSellerDetails>
     <Address>
      <Street1>Industriestrasse 21</Street1>
      <CityName>Friedrichsdorf</CityName>
      <StateOrProvince>default</StateOrProvince>
      <CountryName>Deutschland</CountryName>
      <Phone>0800 35474639</Phone>
      <PostalCode>61381</PostalCode>
      <CompanyName>FLIP4 GmbH</CompanyName>
      <FirstName>Michael</FirstName>
      <LastName>Sauer</LastName>
     </Address>
     <Fax>06172 1794201</Fax>
     <Email>info@flip4new.de</Email>
     <AdditionalContactInformation>Sitz, Registergericht, Handelsregisternummer:  &#xd;
Friedrichsdorf  &#xd;
Amtsgericht Bad Homburg v.d. Höhe  &#xd;
HRB 12472  &#xd;
USt-Id-Nr.: DE264126816  &#xd;
Vertretungsberechtigte Geschäftsführer und&#xd;
verantwortlich für diesen Inhalt: Michael Sauer, Lennart Kleuser</AdditionalContactInformation>
     <TradeRegistrationNumber>Amtsgericht Bad Homburg v.d. Höhe   HRB 12472</TradeRegistrationNumber>
     <LegalInvoice>false</LegalInvoice>
     <TermsAndConditions>Gewährleistung&#xd;
&#xd;
Die Ansprüche des Käufers bei Mängeln richten sich nach den gesetzlichen Regelungen. Wir verkaufen ausschließlich wiederaufbereitete und somit gebrauchte Geräte. Der Lieferumfang richtet sich nach dem in dem jeweiligen Angebot enthaltenen Produktbeschreibung.&#xd;
Für diese Geräte verjähren die Ansprüche des Käufers bei Mängeln mit Ablauf von einem Jahr seit Ablieferung der Sache beim Käufer. Wir haften jedoch unbeschränkt für durch uns, unsere Mitarbeiter und Erfüllungsgehilfen vorsätzlich oder grob fahrlässig verursachte Schäden, bei arglistigem Verschweigen von Mängeln, bei Übernahme einer Beschaffenheitsgarantie sowie für Schäden aus der Verletzung des Lebens, des Körpers oder der Gesundheit.&#xd;
Für sonstige Schäden haften wir nur, sofern eine Pflicht verletzt wird, deren Erfüllung die ordnungsgemäße Durchführung des Vertrages überhaupt erst ermöglicht und auf deren Einhaltung der Vertragspartner regelmäßig vertrauen darf (Kardinalspflicht) und sofern die Schäden aufgrund der vertraglichen Verwendung der Leistungen typisch und vorhersehbar sind. Eine etwaige Haftung nach dem Produkthaftungsgesetz bleibt unberührt. Eine über das Vorstehende hinausgehende Haftung von uns ist ausgeschlossen. &#xd;
&#xd;
&#xd;
Regelungen zum MwSt-Ausweis auf Rechnungen&#xd;
&#xd;
Transaktionen mit gebrauchten und wiederaufbereiteten Geräten unterliegen der Differenzbesteuerung nach §25a UStG. Ein gesonderter Ausweis der Umsatzsteuer für den gebrauchten oder wiederaufbereiteten Gegenstand ist nicht zulässig.&#xd;
&#xd;
Soweit ausdrücklich im Angebotstext vermerkt wird für Neuware und Sonderposten die Mehrwertsteuer in der in Deutschland geltenden Höhe gesondert ausgewiesen.&#xd;
&#xd;
Retouren&#xd;
&#xd;
Vor Rückgabe (bei Widerruf oder Gewährleistungsfall) wird der Käufer gebeten sich an die in der Widerrufsbelehrung angegebene Adresse per E-Mail zu wenden. Es wird dann schnellstmöglich der Rückversand eingeleitet. Zur Kostenübernahme gelten die in der Widerrufsbelehrung gemachten Angaben.&#xd;
&#xd;
&#xd;
Widerrufsbelehrung&#xd;
&#xd;
&#xd;
Widerrufsrecht&#xd;
Sie können Ihre Vertragserklärung innerhalb von 14 Tagen ohne Angabe von Gründen in Textform (z. B. Brief, Fax, E-Mail) oder – wenn Ihnen die Sache vor Fristablauf überlassen wird – durch Rücksendung der Sache widerrufen. Die Frist beginnt nach Erhalt dieser Belehrung in Textform, jedoch nicht vor Eingang der Ware beim Empfänger (bei der wiederkehrenden Lieferung gleichartiger Waren nicht vor Eingang der ersten Teillieferung) und auch nicht vor Erfüllung unserer Informationspflichten gemäß Artikel 246 § 2 in Verbindung mit § 1 Abs. 1 und 2 EGBGB sowie unserer Pflichten gemäß § 312g Abs. 1 Satz 1 BGB in Verbindung mit Artikel 246 § 3 EGBGB. Zur Wahrung der Widerrufsfrist genügt die rechtzeitige Absendung des Widerrufs oder der Sache. &#xd;
&#xd;
Der Widerruf ist zu richten an: &#xd;
&#xd;
Flip4 GmbH &#xd;
Industriestrasse 21&#xd;
61381  Friedrichsdorf  Deutschland  &#xd;
E-Mail: info@flip4new.de&#xd;
&#xd;
Widerrufsfolgen &#xd;
Im Falle eines wirksamen Widerrufs sind die beiderseits empfangenen Leistungen zurückzugewähren und ggf. gezogene Nutzungen (z. B. Zinsen) herauszugeben. Können Sie uns die empfangene Leistung ganz oder teilweise nicht oder nur in verschlechtertem Zustand zurückgewähren, müssen Sie uns insoweit ggf. Wertersatz leisten. Bei der Überlassung von Sachen gilt dies nicht, wenn die Verschlechterung der Sache ausschließlich auf deren Prüfung – wie sie Ihnen etwa im Ladengeschäft möglich gewesen wäre – zurückzuführen ist. Im Übrigen können Sie die Pflicht zum Wertersatz für eine durch die bestimmungsgemäße Ingebrauchnahme der Sache entstandene Verschlechterung vermeiden, indem Sie die Sache nicht wie Ihr Eigentum in Gebrauch nehmen und alles unterlassen, was deren Wert beeinträchtigt. &#xd;
&#xd;
Paketversandfähige Sachen sind auf unsere Gefahr zurückzusenden. Sie haben die Kosten der Rücksendung zu tragen, wenn die gelieferte Ware der bestellten entspricht und wenn der Preis der zurückzusendenden Sache einen Betrag von 40 Euro nicht übersteigt oder wenn Sie bei einem höheren Preis der Sache zum Zeitpunkt des Widerrufs noch nicht die Gegenleistung oder eine vertraglich vereinbarte Teilzahlung erbracht haben. Anderenfalls ist die Rücksendung für Sie kostenfrei. Nicht  paketversandfähige Sachen werden bei Ihnen abgeholt. Verpflichtungen zur Erstattung von Zahlungen müssen innerhalb von 30 Tagen erfüllt werden. Die Frist beginnt für Sie mit der Absendung Ihrer Widerrufserklärung oder der Sache, für uns mit deren Empfang.&#xd;
&#xd;
&#xd;
Bitte beachten Sie desweiteren die rechtlichen Informationen in der Mich Sektion.</TermsAndConditions>
     <VATDetails>
      <VATSite>DE</VATSite>
      <VATID>264126816</VATID>
     </VATDetails>
    </BusinessSellerDetails>
    <IntegratedMerchantCreditCardEnabled>false</IntegratedMerchantCreditCardEnabled>
    <HandlingTime>1</HandlingTime>
    <ConditionID>3000</ConditionID>
    <ConditionDisplayName>Gebraucht</ConditionDisplayName>
    <ExcludeShipToLocation>Africa</ExcludeShipToLocation>
    <ExcludeShipToLocation>Asia</ExcludeShipToLocation>
    <ExcludeShipToLocation>Central America and Caribbean</ExcludeShipToLocation>
    <ExcludeShipToLocation>Middle East</ExcludeShipToLocation>
    <ExcludeShipToLocation>North America</ExcludeShipToLocation>
    <ExcludeShipToLocation>Oceania</ExcludeShipToLocation>
    <ExcludeShipToLocation>Southeast Asia</ExcludeShipToLocation>
    <ExcludeShipToLocation>South America</ExcludeShipToLocation>
    <ExcludeShipToLocation>AL</ExcludeShipToLocation>
    <ExcludeShipToLocation>AD</ExcludeShipToLocation>
    <ExcludeShipToLocation>BA</ExcludeShipToLocation>
    <ExcludeShipToLocation>BG</ExcludeShipToLocation>
    <ExcludeShipToLocation>DK</ExcludeShipToLocation>
    <ExcludeShipToLocation>GI</ExcludeShipToLocation>
    <ExcludeShipToLocation>GR</ExcludeShipToLocation>
    <ExcludeShipToLocation>GG</ExcludeShipToLocation>
    <ExcludeShipToLocation>IS</ExcludeShipToLocation>
    <ExcludeShipToLocation>JE</ExcludeShipToLocation>
    <ExcludeShipToLocation>HR</ExcludeShipToLocation>
    <ExcludeShipToLocation>LV</ExcludeShipToLocation>
    <ExcludeShipToLocation>LI</ExcludeShipToLocation>
    <ExcludeShipToLocation>LT</ExcludeShipToLocation>
    <ExcludeShipToLocation>MT</ExcludeShipToLocation>
    <ExcludeShipToLocation>MK</ExcludeShipToLocation>
    <ExcludeShipToLocation>MD</ExcludeShipToLocation>
    <ExcludeShipToLocation>MC</ExcludeShipToLocation>
    <ExcludeShipToLocation>ME</ExcludeShipToLocation>
    <ExcludeShipToLocation>NO</ExcludeShipToLocation>
    <ExcludeShipToLocation>PT</ExcludeShipToLocation>
    <ExcludeShipToLocation>SM</ExcludeShipToLocation>
    <ExcludeShipToLocation>CH</ExcludeShipToLocation>
    <ExcludeShipToLocation>RS</ExcludeShipToLocation>
    <ExcludeShipToLocation>SJ</ExcludeShipToLocation>
    <ExcludeShipToLocation>UA</ExcludeShipToLocation>
    <ExcludeShipToLocation>HU</ExcludeShipToLocation>
    <ExcludeShipToLocation>VA</ExcludeShipToLocation>
    <ExcludeShipToLocation>BY</ExcludeShipToLocation>
    <TopRatedListing>true</TopRatedListing>
    <GlobalShipping>false</GlobalShipping>
   </Item>
   <Item>
    <BestOfferEnabled>false</BestOfferEnabled>
    <Description>Sie bieten hier auf einen Nikon D90 Body in OVP im sehr guten gebrauchten Zustand Die Kamera beinhaltet alles serienmäßiges Zubehör welches in der OVP mitgeliefert wurde incl. org, Akku, Ladegerät, deutschem Handbuch etc. Die D90 war meine Zweitkamera und wurde immer sehr pfleglich behandelt, demensprechend gut ist der Zustand Das Display wurde stets mit einer Displayschutzfolie versehen und ist nicht verkratzt Auslösezahl des Verschlusses lt. shuttercount ist 20890, ausgelegt ist der Verschluss auf 150tsd Auslösungen mehr Infos zur D90 unter http://www.digitalkamera.de/Testbericht/Nikon_D90/5258.aspx http://img5.fotos-hochladen.net/uploads/kdsc0007ineq7zljcd.jpg http://img5.fotos-hochladen.net/uploads/kdsc0008p3qif74o6m.jpg Privatverkauf: keine Gewährleistung/Umtausch/Geldrückgabe</Description>
    <ItemID>330866234882</ItemID>
    <EndTime>2013-02-06T21:35:02.000Z</EndTime>
    <StartTime>2013-01-30T21:35:02.000Z</StartTime>
    <ViewItemURLForNaturalSearch>http://www.ebay.de/itm/Nikon-D90-Body-Top-Zustand-/330866234882</ViewItemURLForNaturalSearch>
    <ListingType>Chinese</ListingType>
    <Location>Gondenbrett</Location>
    <PaymentMethods>MoneyXferAccepted</PaymentMethods>
    <PaymentMethods>MoneyXferAcceptedInCheckout</PaymentMethods>
    <GalleryURL>http://thumbs3.ebaystatic.com/pict/3308662348828080_1.jpg</GalleryURL>
    <PictureURL>http://i.ebayimg.com/00/s/NzY4WDEwMjQ=/z/aBAAAMXQa7hRCYud/$(KGrHqVHJEIFDzo7(iiSBRCYudO45Q~~60_1.JPG?set_id=880000500F</PictureURL>
    <PostalCode>54595</PostalCode>
    <PrimaryCategoryID>31388</PrimaryCategoryID>
    <PrimaryCategoryName>Foto &amp; Camcorder:Digitalkameras</PrimaryCategoryName>
    <Quantity>1</Quantity>
    <Seller>
     <UserID>ragnotti2011</UserID>
     <FeedbackRatingStar>Turquoise</FeedbackRatingStar>
     <FeedbackScore>158</FeedbackScore>
     <PositiveFeedbackPercent>100.0</PositiveFeedbackPercent>
    </Seller>
    <BidCount>26</BidCount>
    <ConvertedCurrentPrice currencyID="EUR">384.0</ConvertedCurrentPrice>
    <CurrentPrice currencyID="EUR">384.0</CurrentPrice>
    <HighBidder>
     <UserID>p***2</UserID>
     <FeedbackPrivate>false</FeedbackPrivate>
     <FeedbackRatingStar>Yellow</FeedbackRatingStar>
     <FeedbackScore>28</FeedbackScore>
    </HighBidder>
    <ListingStatus>Completed</ListingStatus>
    <QuantitySold>1</QuantitySold>
    <ShipToLocations>DE</ShipToLocations>
    <Site>Germany</Site>
    <TimeLeft>PT0S</TimeLeft>
    <Title>Nikon D90 Body - Top Zustand</Title>
    <ShippingCostSummary>
     <ShippingServiceCost currencyID="EUR">5.0</ShippingServiceCost>
     <ShippingType>Flat</ShippingType>
     <ListedShippingServiceCost currencyID="EUR">5.0</ListedShippingServiceCost>
    </ShippingCostSummary>
    <ItemSpecifics>
     <NameValueList>
      <Name>Marke</Name>
      <Value>Nikon</Value>
     </NameValueList>
     <NameValueList>
      <Name>Produktart</Name>
      <Value>DSLR-Kamera</Value>
     </NameValueList>
     <NameValueList>
      <Name>Herstellergarantie</Name>
      <Value>Keine</Value>
     </NameValueList>
    </ItemSpecifics>
    <HitCount>419</HitCount>
    <PrimaryCategoryIDPath>625:31388</PrimaryCategoryIDPath>
    <Country>DE</Country>
    <ReturnPolicy>
     <ReturnsAccepted>Verbraucher haben das Recht, den Artikel unter den angegebenen Bedingungen zurückzugeben.</ReturnsAccepted>
    </ReturnPolicy>
    <MinimumToBid currencyID="EUR">385.0</MinimumToBid>
    <AutoPay>false</AutoPay>
    <IntegratedMerchantCreditCardEnabled>false</IntegratedMerchantCreditCardEnabled>
    <HandlingTime>2</HandlingTime>
    <ConditionID>3000</ConditionID>
    <ConditionDisplayName>Gebraucht</ConditionDisplayName>
    <GlobalShipping>false</GlobalShipping>
   </Item>
  </GetMultipleItemsResponse>
"""


def test_EbayGetListings_download():
    """Test access to Ebay site and download_xml of XML."""
    from clair.network import EbayGetListings
    from ebay.utils import set_config_file
    
    set_config_file(relative("../python-ebay.apikey"))
    
    #TODO: get IDs with EbayConnector. Fixed IDs will expire.
    ids = pd.Series(["271149493368", "330866234882", "140914051088", "221185477679"])
    
    g = EbayGetListings()
    xml = g.download_xml(ids)
    print xml
    
    root = etree.fromstring(xml)
#    print etree.tostring(root, pretty_print=True)
    ack = root.find("{urn:ebay:apis:eBLBaseComponents}Ack").text
    assert ack == "Success"


def test_EbayGetListings_parse():
    """Test access to Ebay site and download_xml of XML."""
    from clair.network import EbayGetListings

    g = EbayGetListings()
    listings = g.parse_xml(EBAY_GetMultipleItemsResponse_RESPONSE)
    
    print listings
    print
    print listings[["title", "price", "sold", "active"]].to_string()
    
    #There are two listings (items) in the response
    assert len(listings) == 4


def test_EbayGetListings_get_listings():
    """Test access to Ebay site and download_xml of XML."""
    from clair.network import EbayGetListings
    from ebay.utils import set_config_file
    
    set_config_file(relative("../python-ebay.apikey"))
    
    #TODO: get IDs with EbayConnector. Fixed IDs will expire.
    ids = pd.Series(["271149493368", "330866234882", "140914051088", "221185477679"])
    
    g = EbayGetListings()
    listings = g.get_listings(ids)
    print listings
    print
    print listings[["title", "price", "sold", "active"]].to_string()
    
    #There are two listings (items) in the response
    assert len(listings) == 4


#---- EbayConnector --------------------------------------------------------- 
   
def test_EbayConnector_find_listings():
    """Test finding listings by keyword through the high level interface."""
    from clair.network import EbayConnector
    
    c = EbayConnector(relative("../python-ebay.apikey"))
    listings = c.find_listings(keywords="Nikon D90", n_listings=5)
    
#    print listings
    print listings[["title", "price", "currency"]].to_string()
    print
    assert 0.8 * 5 <= len(listings) <= 5 #Duplicates are removed


def test_EbayConnector_update_listings():
    """Test finding listings by keyword through the high level interface."""
    from clair.network import EbayConnector
    
    n = 35
    
    c = EbayConnector(relative("../python-ebay.apikey"))
    listings = c.find_listings(keywords="Nikon D90", 
                               n_listings=n, 
                               min_price=100, max_price=500, currency="EUR")
    print listings
    print
    print listings[["title", "price", "sold", "active"]].to_string()

    #The test
    listings =c.update_listings(listings)
    
    print
    print listings
    print
    print listings[["title", "price", "sold", "active"]].to_string()

    assert 0.95 * n <= len(listings) <= n #Duplicates are removed
   

if __name__ == '__main__':
#    test_convert_ebay_condition()
#    test_EbayFindListings_download()
#    test_EbayFindListings_parse()
#    test_EbayFindListings_find()
    
#    test_EbayGetListings_download()
#    test_EbayGetListings_parse()
#    test_EbayGetListings_get_listings()
    
#    test_EbayConnector_find_listings()
    test_EbayConnector_update_listings()
    
    pass #pylint: disable=W0107
