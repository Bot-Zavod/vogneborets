var stripe = Stripe('pk_test_3LtOdozoRiUg6rH7Jtn5k8tR008gczBxTM');
var elements = stripe.elements();

// Set up Stripe.js and Elements to use in checkout form
var style = {
  base: {
    color: "#32325d",
  }
};

var card = elements.create("card", { style: style });
card.mount("#card-element");