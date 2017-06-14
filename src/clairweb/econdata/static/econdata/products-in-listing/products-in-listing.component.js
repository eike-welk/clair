
'use strict';

// Register `productsInListing` component, along with its associated controller 
// and template
angular.
    module('productsInListing').
    component('productsInListing', {
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
//                console.log("Listing ID: " + ctrl.listingId);
                ctrl.getProducts();
            };
            
            // Fill `ctrl.productsInListing` from database table 'products-in-listings'.
            // Replace the product URL with the assocated product object from
            // `ctrl.productsMany`.
            ctrl.getProducts = function(iPage=1) {
                $http
                .get("/econdata/api/products-in-listings/", 
                     {params: {listing: ctrl.listingId, page: iPage}})
                .then(function(response){
                    // If this is the first page, delete the array.
                    if (iPage === 1) {
                        ctrl.productsInListing = [];
                    }

                    for (var pilRecord of response.data.results) {
                        // Find the product, that is associated to the URL.
                        var urlParts = pilRecord.product.split("/");
                        var productID = urlParts.slice(-2)[0];
                        var product = ctrl.productsMany.find(function(product){
                            return product.id === productID;});
                        // Replace the URL by the product, and store the 
                        // modified products-in-listing record.
                        pilRecord.product = product;
                        ctrl.productsInListing.push(pilRecord);
                    }

                    // Get next page if it exists.
                    if (response.data.next !== null) {
                        ctrl.getProducts(iPage + 1);
                    }
                });
            };
            
            // Store (in DB) that a product appears in a listing. 
            // This information will be used as training data.
            ctrl.addProduct = function(productName) {
                console.log("Add product: " + productName);
                // Find the product with the given name
                var product = ctrl.productsMany.find(function(product){
                    return product.name === productName;});
                // Store that product is contained in listing
                if (product !== undefined) {
                    console.log('Found product');
                    $http
                    .post('/econdata/api/products-in-listings/',
                          {product: '/econdata/api/products/' + product.id + '/', 
                           listing: '/econdata/api/listings/' + ctrl.listingId + '/',
                           is_training_data: true})
                    .then(function(_response){
                        // After data is stored, refresh `ctrl.productsInListing`
                        ctrl.getProducts();
                    });
                }
            };
            
            ctrl.removeProduct = function(recordID) {
                console.log("Remove product: " + recordID);
            };
        }]
    });