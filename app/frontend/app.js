// app.js

// -------------------------------------------------------------------
// Backend API URLs for Ingress-based routing
// -------------------------------------------------------------------
const PRODUCTS_API_URL = "/api/products";


// -------------------------------------------------------------------
// DOM references
// -------------------------------------------------------------------
const loadProductsButton = document.getElementById("load-products-button");
const createProductButton = document.getElementById("create-product-button");

const statusBox = document.getElementById("status-box");
const productsList = document.getElementById("products-list");

const productNameInput = document.getElementById("product-name-input");
const productPriceInput = document.getElementById("product-price-input");


// -------------------------------------------------------------------
// Helper function to clear rendered products
// -------------------------------------------------------------------
function clearProductsList() {
    productsList.innerHTML = "";
}


// -------------------------------------------------------------------
// Helper function to render products on the page
// -------------------------------------------------------------------
function renderProducts(products) {
    // Clear existing product cards before rendering fresh data.
    clearProductsList();

    // Render one list item per product.
    products.forEach((product) => {
        const listItem = document.createElement("li");
        listItem.className = "product-card";

        const productName = document.createElement("div");
        productName.className = "product-name";
        productName.textContent = product.name;

        const productPrice = document.createElement("div");
        productPrice.className = "product-price";
        productPrice.textContent = `Price: ₹${product.price}`;

        listItem.appendChild(productName);
        listItem.appendChild(productPrice);

        productsList.appendChild(listItem);
    });
}


// -------------------------------------------------------------------
// Fetch products from backend and render them
// -------------------------------------------------------------------
async function loadProducts() {
    statusBox.textContent = "Loading products from backend...";
    clearProductsList();

    try {
        const response = await fetch(PRODUCTS_API_URL);

        if (!response.ok) {
            throw new Error(`Backend returned HTTP ${response.status}`);
        }

        const products = await response.json();
        renderProducts(products);

        statusBox.textContent = "Products loaded successfully.";
    } catch (error) {
        statusBox.textContent = `Failed to load products: ${error.message}`;
    }
}


// -------------------------------------------------------------------
// Create a new product through backend API
// -------------------------------------------------------------------
async function createProduct() {
    // Read values from form inputs.
    const productName = productNameInput.value.trim();
    const productPriceValue = productPriceInput.value.trim();

    // Basic validation so we do not send empty data.
    if (!productName) {
        statusBox.textContent = "Product name is required.";
        return;
    }

    if (!productPriceValue) {
        statusBox.textContent = "Product price is required.";
        return;
    }

    const productPrice = Number(productPriceValue);

    if (Number.isNaN(productPrice) || productPrice <= 0) {
        statusBox.textContent = "Product price must be a positive number.";
        return;
    }

    statusBox.textContent = "Creating product...";

    try {
        const response = await fetch(PRODUCTS_API_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                name: productName,
                price: productPrice,
            }),
        });

        if (!response.ok) {
            throw new Error(`Backend returned HTTP ${response.status}`);
        }

        const createdProduct = await response.json();

        // Clear form after successful creation.
        productNameInput.value = "";
        productPriceInput.value = "";

        statusBox.textContent = `Created product: ${createdProduct.name}`;

        // Reload products so the new product appears immediately in the UI.
        await loadProducts();
    } catch (error) {
        statusBox.textContent = `Failed to create product: ${error.message}`;
    }
}


// -------------------------------------------------------------------
// Register button click handlers
// -------------------------------------------------------------------
loadProductsButton.addEventListener("click", loadProducts);
createProductButton.addEventListener("click", createProduct);