// 두 입력 필드의 내용을 확인하여 버튼 활성화 여부를 결정하는 함수
function checkInputFilled() {
    var urlValue = document.getElementById('url').value.trim(); // trim()을 사용하여 공백 제거
    var nameValue = document.getElementById('name').value.trim();

    var addButton = document.getElementById('addButton');
  
    if (urlValue !== "" && nameValue !== "") {
      addButton.removeAttribute('disabled'); // 두 필드가 모두 채워졌을 때 버튼 활성화
    }
  }