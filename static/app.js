const form = document.querySelector('#form');

form.addEventListener('submit', function (e) {
    e.preventDefault();
    getColors()

})

function getColors() {
    const query = form.elements.query.value;
    // This is the way to send data in a form shape
    fetch('/palette', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: new URLSearchParams({
            query: query
        })
    })
        .then((response) => response.json())
        .then(data => {
            const { colors } = data;
            const container = document.querySelector('.container');
            createColorBoxes(colors, container)

        })
}


function createColorBoxes(colors, container) {
    container.innerHTML = '';
    for (const color of colors) {
        const div = document.createElement('div')
        div.classList.add('color')
        div.style.backgroundColor = color;
        div.style.width = `calc(100%/${colors.length})`

        div.addEventListener('click', function () {
            navigator.clipboard.writeText(color)
        })

        const span = document.createElement('span');
        span.innerHTML = color;
        div.appendChild(span);
        container.appendChild(div)
    }
}
