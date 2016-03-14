<script>
var canonicalOrigin = "${canonical_origin}";

var postMessage = function(data) {
    window.parent.postMessage(JSON.stringify(data), canonicalOrigin);
};

var onMessage = function(name, cb) {
    window.addEventListener("message", function(event) {
        if (event.origin === canonicalOrigin) {
            var message = JSON.parse(event.data);
            if (message.name === name) {
                cb(message);
            }
        }
    });
}
</script>
