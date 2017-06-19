'use strict';

// Define the `productsApp` module
angular.module('productsApp',
               ['productsList'])
       .config(['$httpProvider', function ($httpProvider) {
            // Configure usage of Django's CSRF token.
            $httpProvider.defaults.xsrfCookieName = 'csrftoken';
            $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
       }]);
