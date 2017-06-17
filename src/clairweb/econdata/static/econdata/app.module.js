'use strict';

// Define the `econdataApp` module
angular.module('econdataApp', 
               ['listingsList', 'productsInListing'])
       .config(['$httpProvider', function ($httpProvider) {
            // Configure usage of Django's CSRF token.
            $httpProvider.defaults.xsrfCookieName = 'csrftoken';
            $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
       }]);

