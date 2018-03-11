'use strict';

// Define the `searchTasksApp` module
angular.module('searchTasksApp',
               ['searchTasksList'])
       .config(['$httpProvider', function ($httpProvider) {
            // Configure usage of Django's CSRF token.
            $httpProvider.defaults.xsrfCookieName = 'csrftoken';
            $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
       }]);
