const auth = require('./auth');
const vehicles = require('./vehicles');
const customers = require('./customers');
const sales = require('./sales');
const rateLimit = require('./rateLimit');

module.exports = {
  auth,
  vehicles,
  customers,
  sales,
  rateLimit
};
