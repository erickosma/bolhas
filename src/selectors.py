TITLE_SELECTORS = [
    "h1.product-title",
    "h1.product-name",
    "h1#productTitle",
    "[data-testid='product-title']",
    "h1",
    ".product-title",
]

PRICE_SELECTORS = [
    ".price",
    ".product-price",
    "#priceblock_ourprice",
    "[data-testid='price']",
    ".offer-price",
    "span.price",
]

DESCRIPTION_SELECTORS = [
    ".product-description",
    "#productDescription",
    "[data-testid='product-description']",
    ".description",
    "#feature-bullets",
    "meta[name='description']",
]

IMAGE_SELECTORS = [
    "#landingImage",
    "#imgBlkFront",
    "[data-testid='product-image'] img",
    ".product-image img",
    ".product-gallery img",
    "#product-image img",
    ".gallery-image img",
    "[data-zoom-image]",
    "img.product-image",
    "img[data-src]",
]

COOKIE_ACCEPT_SELECTORS = [
    "#sp-cc-accept",
    "#onetrust-accept-btn-handler",
    "[data-testid='cookie-accept']",
    "button[id*='cookie']",
    "button[id*='accept']",
]

IMAGE_PRIORITY_ATTRIBUTES = [
    "data-zoom-image",
    "data-old-hires",
    "data-src",
    "src",
]

IMAGE_IGNORE_PATTERNS = [
    "placeholder",
    "icon",
    "sprite",
    "1x1",
    "pixel",
    "blank",
]
