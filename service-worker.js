self.addEventListener("install", e => {

e.waitUntil(

caches.open("mercearia")

.then(cache => {

return cache.addAll([
"/",
"index.html",
"style.css",
"app.js",
"dados.json"
])

})

)

})
