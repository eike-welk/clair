'use strict';

// Register `productsList` component, along with its associated controller and template
angular.
  module('productsList').
  component('productsList', {
    templateUrl: '/static/econdata/products-list/products-list.template.html',
    controller: ['$http', function productsListController($http) {
      var ctrl = this;
      ctrl.orderProp = '';
      ctrl.products = [];

      ctrl.$onInit = function() {
        ctrl.getProducts();
      };

      ctrl.getProducts = function (iPage = 1) {
        if(iPage === 1) {
          ctrl.products = [];
        }
        $http
        .get('/econdata/api/products/', {params: {page: iPage}})
        .then(function (response) {
          ctrl.products = ctrl.products.concat(response.data.results);

          if (response.data.next !== null) {
            ctrl.getProducts(iPage + 1);
          }
        });
      };

    }]
  });
