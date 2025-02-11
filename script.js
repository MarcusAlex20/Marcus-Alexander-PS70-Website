document.addEventListener('DOMContentLoaded', () => {
    const nameElement = document.getElementById('name');
    const nameText = "Marcus Alexander";
    let index = 0;

    function typeTitle() {
        if (index < nameText.length) {
            nameElement.textContent += nameText.charAt(index);
            index++;
            setTimeout(typeTitle, 100);
        }
    }

    typeTitle();

    document.addEventListener('mousemove', (e) => {
        const binaryCode = document.createElement('div');
        binaryCode.className = 'binary-code';
        binaryCode.textContent = '010101';
        binaryCode.style.left = `${e.pageX}px`;
        binaryCode.style.top = `${e.pageY}px`;
        document.body.appendChild(binaryCode);

        setTimeout(() => {
            binaryCode.remove();
        }, 2000);
    });
});
