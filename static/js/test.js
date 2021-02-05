
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
    $(element).css({'background':'gray'})
    return element_disabled
}
function button_RemoveDisabeld(element){// 取消置灰{
    var element_remove  = $(element).removeAttr('disabled');
    $(element).removeAttr('style') 
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

function PickMeUp(event){
    var targe_name = event.target.className;
    if (targe_name == "start_time" || targe_name == "end_time" ){
        if ($('.pmu-instance').length == 0){
        var datesFromDatabase = [];
        pickmeup('.example',{
        flat: true,
        mode: 'single',
        locale:'en',
        hide_on_select: true,
        position :'right',
        // Before rendering dates, highlight if from database
        render: function(date) {
            if ($.inArray(date.getTime(), datesFromDatabase) > -1){
                return {
                    class_name : ''
                }
            }
        }
        });
        var check = targe_name+"_check";//確認按鈕
        $('.pmu-instance').after('<div class="check_submit" ><input type="button" value="確認" class="'+ check + '"></div>')
        $('.'+check).css({
            "background": "#ffe086",
            "color": "#7a0e8c",
            "font-family": "unset",
            "margin-left": "40%",
        })
        if(targe_name=='end_time'){
            $('.example').css({
            "margin-left": "12.7%"
            })
        }
        else{
            $('.example').css({
            "margin-left": ".4%"
            })
        }
        
        return false;
        }
        var child_name = $('.check_submit').children()[0].className // 或者 子元素的 確認按鈕
        if (child_name.indexOf(targe_name)==-1){// 為-1 ,代表初始化 的確認按鈕,和 當下點擊的 按鈕 名稱不同
            $('.'+child_name).attr('class',targe_name+"_check")
        }
        $('.example').show()
        if(targe_name=='end_time'){
            $('.example').css({
            "margin-left": "12.7%"
            })
        }
        else{
            $('.example').css({
            "margin-left": ".4%"
            })
        }
    }
    else if (targe_name=='start_time_check' || targe_name=='end_time_check' ){//確認按鈕 , 要把text更新
        var select_year = $('.pmu-years > .pmu-selected.pmu-button').text()
        var select_month = $('.pmu-months > .pmu-selected.pmu-button').text()
        var select_day = $('.pmu-days > .pmu-selected.pmu-button').text()
        $('.example').hide()
        if(targe_name == "start_time_check" ){
            $('.start_time').val(select_year+"-"+select_month+"-"+select_day)  
        }
        else{
            $('.end_time').val(select_year+"-"+select_month+"-"+select_day)  
        }
           
    }
    else if (targe_name== "" || targe_name=="example"){//空白處
        $('.example').hide()  
    }
}

