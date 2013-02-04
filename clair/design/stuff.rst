########################################
                Stuff
########################################

Online Price Discovery Project


Project Name
========================================

Find nice name for the project. It is currently named `Clair` after Wesley
Clair Mitchell. Here are some other ideas:

* Price Charts
    Maybe good name for the price chart program.
* Price History
* Second Hand Market Helper
* Used Goods Price Helper
* Price Data Explorer
* Online Price Collector
* Online Trade Explorer
* Online Price Discovery Project
* Econometrics for Used Goods
* Online Econometrics
* $Name of person who was famous in area of econometrics/used goods/sustainable development
    * Arthur Hanau
        First description of pork cycles.
    * Ragnar Frisch
        Founded discipline of econometrics
    * Joseph Schumpeter
        Important economist, and econometrist. Also sympathetic figure. 
    * Frank William Taussig
        Founder of modern trade theory. Also somewhat sympathetic figure. 
        Seems less important than many others in the list, so using his name
        will probably anger no one.
    * Wesley Clair Mitchell
        Important economist, worked empirically on business cycles.
        Believed strongly that markets need to be regulated.


Find Ebay Product IDs
========================================

The following code searches for Ebay product IDs::

        #Find product ID of an iPod (Nano, 5th generation black)
        from ebay.shopping import FindProducts
        global productId
        
        result = FindProducts(query="ipod nano", available_items=False, 
                              max_entries=20, encoding="XML")
        print result
        root = etree.fromstring(result)
        for product in root.iter("{urn:ebay:apis:eBLBaseComponents}Product"):
        #    print etree.tostring(product)
            title = product.find("{urn:ebay:apis:eBLBaseComponents}Title").text
        #    print title
            if title.find("Black") != -1 and title.find("5th Generation") != -1:
                print "Found desired product"
                print title
                product_id = product.find("{urn:ebay:apis:eBLBaseComponents}ProductID").text 
                print "ID = ", product_id
                print
                productId = "ePID:" + product_id
                break

