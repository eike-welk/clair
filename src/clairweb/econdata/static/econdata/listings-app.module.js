'use strict';

// Define the `listingsApp` module
angular.module('listingsApp', 
               ['listingsList', 'productsInListing'])
       .config(['$httpProvider', function ($httpProvider) {
            // Configure usage of Django's CSRF token.
            $httpProvider.defaults.xsrfCookieName = 'csrftoken';
            $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
       }]);

