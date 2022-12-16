const favorites = (el, id) => {
    $.ajax({
        type: "POST",
        url: '/to-favorites',
        data: {id: id},
        success: el.classList.toggle('favorites-added')
    });
}

const cart = (id) => {
    $.ajax({
        type: "POST",
        url: '/add-to-cart',
        data: {id: id},
        success: alert("Товар добавлен в корзину")
    });
}