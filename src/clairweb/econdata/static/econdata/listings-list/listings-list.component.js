'use strict';

// Register `listingsList` component, along with its associated controller and template
angular.
  module('listingsList').
  component('listingsList', {
    templateUrl: '/static/econdata/listings-list/listings-list.template.html',
    controller: ['$http', function listingsListController($http) {
      var self = this;
      self.orderProp = 'time';
      self.listings = [];

      $http.get('/econdata/api/listings/').then(function(response) {
        self.listings = response.data.results;
      });
    }]
  });
