
'use strict';

// Register `productsInListing` component, along with its associated controller and template
angular.
    module('productsInListing').
    component('productsInListing', {
        templateUrl: '/static/econdata/products-in-listing/products-in-listing.template.html',
        controller: ['$http', function productsInListingController($http) {
            var self = this;
            console.log("Listing ID: " + self.listingId);
        }],
        bindings: {
            listingId: "@"
        }
    });