
'use strict';

// Register `productsInListing` component, along with its associated controller
// and template
angular
.module('productsInListing')
.component('productsInListing', {
    templateUrl: '/static/econdata/products-in-listing/products-in-listing.template.html',
    bindings: {
        listingId: "@",
        productsMany: "<",
        productsFew: "<"
    },
    controller: ['$http', function productsInListingController($http) {
        var ctrl = this;
        ctrl.productsInListing = [];

        ctrl.$onInit = function() {
            //Add entry to drop down control, for "No interesting products"
            ctrl.productsFew = [{name: ""}].concat(ctrl.productsFew);
            ctrl.getProducts();
        };

        /**
         * Fill `ctrl.productsInListing` from DB table 'products-in-listings'.
         *
         * Look up the name of the product in the DB.
         * Fill `ctrl.productsInListing` from DB table `productsInListings`.
         *
         * @param {Number} iPage - Page number, the API is paginated.
         */
        ctrl.getProducts = function(iPage=1) {
            $http
            .get("/econdata/api/products-in-listings/",
                 {params: {listing: ctrl.listingId, page: iPage}})
            .then(function(response){
                // If this is the first page, delete the array.
                if (iPage === 1) {
                    ctrl.productsInListing = [];
                }

                // Find the product, that is associated to the `product` URL.
                var productsInListingDB = response.data.results;
                productsInListingDB.forEach(function(pilRecord) {
                    if (pilRecord.product === null) {
                        // If the record contains no product URL, create a dummy
                        // product name
                        pilRecord.productName = "<No Products>";
                        ctrl.productsInListing.push(pilRecord);
                    } else {
                        // Follow the product URL and get the product from the DB
                        $http
                        .get(pilRecord.product)
                        .then(function(response){
                            // Store the product name in the `productsInListing` record
                            var product = response.data;
                            pilRecord.productName = product.name;
                            ctrl.productsInListing.push(pilRecord);
                        });
                    }
                });

                // Get next page if it exists.
                if (response.data.next !== null) {
                    ctrl.getProducts(iPage + 1);
                }
            });
        };

        /**
         * Store that a product appears in a listing.
         *
         * The new record is always marked as training data.
         *
         * @param {String} productName
         */
        ctrl.addProduct = function(productName) {
            console.log("Add product: '" + productName + "'");
            var product;
            if (productName === "" || productName === undefined) {
                // The user wants to add a record with no product.
                // to express that the listing contains no interesting products.
                product = null;
            } else {
                // Find the product with the given name
                product = ctrl.productsMany.find(function(product){
                    return product.name === productName;});
                if (product === undefined) {
                    return;
                }
                console.log('Found product: ' + product.id);
            }

            // Create the `products-in-listings` record
            $http
            .post('/econdata/api/products-in-listings/',
                  {product: product === null ? null :
                            '/econdata/api/products/' + product.id + '/',
                   listing: '/econdata/api/listings/' + ctrl.listingId + '/',
                   is_training_data: true})
            .then(function(_response){
                // After data is stored, refresh `ctrl.productsInListing`
                ctrl.getProducts();
            });
        };

        /**
         * Remove record that a product appears in a listing.
         *
         * @param {String} recordID - The ID of the record in the DB table.
         */
        ctrl.removeProduct = function(recordID) {
            console.log("Remove product: " + recordID);
            $http
            .delete('/econdata/api/products-in-listings/' + recordID + '/')
            .then(function(response){
                // After the record is deleted, refresh `ctrl.productsInListing`
                ctrl.getProducts();
            });
        };
    }]
});