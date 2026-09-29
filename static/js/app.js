const form =
    document.getElementById("comic-form");


if (form) {

    form.addEventListener(
        "submit",
        () => {

            const button =
                document.getElementById(
                    "generate-button"
                );

            const label =
                document.getElementById(
                    "button-label"
                );

            const spinner =
                document.getElementById(
                    "spinner"
                );


            button.disabled = true;

            label.textContent =
                "Creating your comic...";

            spinner.classList.remove(
                "hidden"
            );

        }
    );

}