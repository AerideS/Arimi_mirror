let noticeBtnCount = 1;

function create_noticeTag() {
    let tagArea = document.getElementById('tagArea');
    let new_li = document.createElement('li');
    let new_noticeTag = document.createElement('a');

    new_noticeTag.setAttribute('class', 'noticeTag');
    new_noticeTag.setAttribute('href', document.getElementById('url').value);
    new_noticeTag.setAttribute('target', 'blank');
    new_noticeTag.innerHTML = document.getElementById('name').value;
    
    //아래 방법으로 링크 걸기도 가능
    // new_noticeTag.onclick = function() {
    //     // 새 창에서 URL 열기
    //     window.open('https://www.gnu.ac.kr/anse/na/ntt/selectNttList.do?mi=3041&bbsId=1383');
    // };

    tagArea.appendChild(new_li);
    new_li.appendChild(new_noticeTag);

    noticeBtnCount++;
}