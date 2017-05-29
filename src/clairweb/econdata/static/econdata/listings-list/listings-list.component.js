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
      self.iGet = 1;
      
      self.getListings = function() {
        $http.get('/econdata/api/listings/', {params: {'page': self.iGet}})
          .then(function(response) {
            self.listings = self.listings.concat(response.data.results);
          });
        self.iGet += 1;
      }

      self.getListings();
    }]
  });
