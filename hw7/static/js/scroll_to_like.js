window.onload = function () {
    if (window.location.hash === '#postFooter') {
        let postFooter = document.getElementById('postFooter');
        postFooter.scrollIntoView();
    }
    if (window.location.hash === '#comments') {
        let commentsFooter = document.getElementById('comments');
        commentsFooter.scrollIntoView();
    }
    if (window.location.hash.includes('#likeComment')) {
        let commentFooter = document.getElementById(window.location.hash.slice(1));
        if (commentFooter) {
            commentFooter.scrollIntoView();
        }
    }
}
