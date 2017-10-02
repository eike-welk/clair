'use strict';

// Register `searchTasksList` component, along with its associated controller and template
angular.
  module('searchTasksList').
  component('searchTasksList', {
    templateUrl: '/static/collect/search-tasks-list/search-tasks-list.template.html',
    controller: ['$http', function searchTasksListController($http) {
      var ctrl = this;
      ctrl.orderProp = '';
      ctrl.searchTasks = [];

      ctrl.$onInit = function() {
        ctrl.getProducts();
      };

      ctrl.getProducts = function (iPage = 1) {
        if(iPage === 1) {
          ctrl.searchTasks = [];
        }
        $http
        .get('/collect/api/search_tasks/', {params: {page: iPage}})
        .then(function (response) {
          ctrl.searchTasks = ctrl.searchTasks.concat(response.data.results);

          if (response.data.next !== null) {
            ctrl.getProducts(iPage + 1);
          }
        });
      };

    }]
  });
