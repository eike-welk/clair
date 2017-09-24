'use strict';

// Define the `pricesApp` module
angular.module('pricesApp',
               ['pricesList'])
       .config(['$httpProvider', function ($httpProvider) {
            // Configure usage of Django's CSRF token.
            $httpProvider.defaults.xsrfCookieName = 'csrftoken';
            $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
       }]);
