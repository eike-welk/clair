
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

                // TODO: Find different solution
                // * Either follow the `product` link in each record and get
                //   product name from there, or...
                // * Create an other API, which contains all the necessary
                //   information. This would shift some of the complexity to
                //   the Python side.
                for (var pilRecord of response.data.results) {
                    // Find the product, that is associated to the URL.
                    var product;
                    if (pilRecord.product === null) {
                        // If the record contains no product, create a dummy product.
                        product = {name: "<No Products>"};
                    } else {
                        // Find the product in the product array for the text
                        // completion.
                        var urlParts = pilRecord.product.split("/");
                        var productID = urlParts.slice(-2)[0];
                        product = ctrl.productsMany.find(function(product){
                            return product.id === productID;});
                    }
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

        // Remove from DB that a  product appears in a listing.
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