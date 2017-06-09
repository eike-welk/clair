
'use strict';

// Register `productsInListing` component, along with its associated controller and template
angular.
    module('productsInListing').
    component('productsInListing', {
        templateUrl: '/static/econdata/products-in-listing/products-in-listing.template.html',
        bindings: {
            listingId: "@",
            productsMany: "<",
            productsFew: "<",
        },
        controller: ['$http', function productsInListingController($http) {
            var ctrl = this;

            ctrl.$onInit = function() {
                console.log("Listing ID: " + ctrl.listingId);
                console.log("productsMany: " + ctrl.productsMany.length);
                console.log("productsFew: " + ctrl.productsFew.length);
            };
            
            ctrl.addProduct = function(productName) {
                console.log("Add product: " + productName);
            }
        }],
    });