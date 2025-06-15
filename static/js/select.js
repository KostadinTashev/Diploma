document.addEventListener('DOMContentLoaded', function () {
    const mealContainer = document.getElementById('meals-container');
    const addMealBtn = document.getElementById('add-meal');
    const mealTemplate = document.getElementById('empty-meal-form').innerHTML;
    const foodTemplate = document.getElementById('empty-food-form').innerHTML;

    let mealIndex = document.querySelectorAll('.meal-block').length;

    addMealBtn.addEventListener('click', function () {
        const html = mealTemplate.replace(/__prefix__/g, mealIndex).replace(/__number__/g, mealIndex + 1);
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = html;
        const mealBlock = tempDiv.firstElementChild;

        mealContainer.appendChild(mealBlock);
        attachMealEvents(mealBlock);

        mealIndex++;
    });

    document.querySelectorAll('.meal-block').forEach(block => attachMealEvents(block));

    function attachMealEvents(mealBlock) {
        const addFoodBtn = mealBlock.querySelector('.add-food');
        const foodsContainer = mealBlock.querySelector('.foods-container');
        let foodIndex = foodsContainer.querySelectorAll('.food-item').length;

        addFoodBtn.addEventListener('click', function () {
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = foodTemplate;
            const foodItem = tempDiv.firstElementChild;

            foodItem.querySelectorAll('input, select, textarea').forEach(input => {
                if (input.name) input.name = input.name.replace('__prefix__', foodIndex);
                if (input.id) input.id = input.id.replace('__prefix__', foodIndex);
            });

            foodsContainer.appendChild(foodItem);
            attachAutocomplete(foodItem.querySelector('.product-name-input'), foodItem.querySelector('.product-id-input'));
            attachRemoveFood(foodItem);
            foodIndex++;
        });

        mealBlock.querySelector('.remove-meal')?.addEventListener('click', function () {
            mealBlock.remove();
        });

        foodsContainer.querySelectorAll('.food-item').forEach(foodItem => {
            attachAutocomplete(foodItem.querySelector('.product-name-input'), foodItem.querySelector('.product-id-input'));
            attachRemoveFood(foodItem);
        });
    }

    function attachRemoveFood(foodItem) {
        foodItem.querySelector('.remove-food')?.addEventListener('click', function () {
            foodItem.remove();
        });
    }

    function attachAutocomplete(textInput, hiddenInput) {
        if (!textInput) return;

        textInput.addEventListener('input', function () {
            const query = this.value;

            fetch(`/autocomplete_products/?q=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    const datalistId = `products-${Math.random().toString(36).substring(2, 8)}`;
                    let datalist = document.getElementById(datalistId);

                    if (!datalist) {
                        datalist = document.createElement('datalist');
                        datalist.id = datalistId;
                        document.body.appendChild(datalist);
                        textInput.setAttribute('list', datalistId);
                    }

                    datalist.innerHTML = '';
                    data.forEach(product => {
                        const option = document.createElement('option');
                        option.value = product.name;
                        option.dataset.id = product.id;
                        datalist.appendChild(option);
                    });

                    textInput.addEventListener('change', function () {
                        const selectedOption = [...datalist.options].find(opt => opt.value === textInput.value);
                        if (selectedOption) {
                            hiddenInput.value = selectedOption.dataset.id;
                        } else {
                            hiddenInput.value = '';
                        }
                    });
                });
        });
    }
});
