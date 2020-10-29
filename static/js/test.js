
function pretty(js_path,split_){ //dataframe調整 文字版面 , js_path為element js定位, split_: 切各字元
    try{
        game_explan = document.querySelector(js_path)//
        explan_1 = game_explan.textContent.split(split_)[0]//用 #來分割
        explan_2 = game_explan.textContent.split(split_)[1]// #後
        game_explan.innerHTML = explan_1 + "<br>" +"<span>"+split_+explan_2+"</span>" //換行 ,增加span
    }
    catch{
        return false;
    }
}
function remote_IP(){ // 在頁面,呼叫是哪個ip
    var ip = returnCitySN["cip"]+','+returnCitySN["cname"]
    console.log(ip)
    $.post(
        url = '/remote_IP',
        data = ip
    )
}
function form_trim(form_element){ // 輸入框,去除 空白
    var form = $(form_element);
    var formArr = form. serializeArray();
    jQuery.each(formArr , function(i, field) {
    formArr[i].value = $.trim(field.value);
    });
    var serializedForm = $.param(formArr);
    return serializedForm
}

function button_disabled(element){// 按扭送出後  置灰
    var element_disabled = $(element).attr('disabled','true');
    return element_disabled
}
function button_RemoveDisabeld(element){// 取消置灰{
    var element_remove  = $(element).removeAttr('disabled');
    return element_remove
}

function addOption(selectbox, text, value) {//初始頁面後, 月份/日期 option ,value,text 直接 顯示
    var option = document.createElement("option");
    option.text = text;
    option.value = value;
    selectbox.options.add(option);
}
function toCurrency(num){// 轉換成 數值字元
    var par = num.toString().split('.')
    par[0] = par[0].replace(/\B(?=(\d{3})+(?!\d))/g, ',')// 數字符號
    return par.join('.')
}
