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
      self.iListingsPage = 1;
      self.products = [];
      
      self.getListings = function() {
        $http.get('/econdata/api/listings/', {params: {'page': self.iListingsPage}})
          .then(function(response) {
            self.listings = self.listings.concat(response.data.results);
          });
        self.iListingsPage += 1;
      };

      self.getProducts = function(iPage=1) {
        $http.get('/econdata/api/products/', {params: {'page': iPage}})
          .then(function(response) {
            self.products = self.products.concat(response.data.results);
            if (response.data.next !== null) {
                self.getProducts(iPage + 1);
            }
          });
      };

      self.$onInit = function() {
        self.getListings();
        self.getProducts();
      };
    }]
  });
