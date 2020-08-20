
/*
document.writeln("<div class=\'btn-group\'>");
document.writeln("        <button type=\'button\' class=\'btn btn-primary dropdown-toggle dropdown-toggle-split\' data-toggle=\'dropdown\' aria-haspopup=\'true\' aria-expanded=\'false\'>");
document.writeln("          體育");
document.writeln("        </button>");
document.writeln("        <div class=\'dropdown-menu\'>");
document.writeln("          <a class=\'dropdown-item\' href=\'sb\'>沙巴體育比分</a>");
document.writeln("          <a class=\'dropdown-item\' href=\'sbApi\'>沙巴體育API</a>");
document.writeln("          <a class=\'dropdown-item\' href=\'sport\'>企鵝網體育比分</a>");
document.writeln("          <a class=\'dropdown-item\' href=\'sportApi\'>企鵝體育API</a>");
document.writeln("        </div>");
document.writeln("    </div>");*/
document.writeln("    <div class=\'btn-group\'>");
document.writeln("        <button type=\'button\' class=\'btn btn-primary dropdown-toggle dropdown-toggle-split\' data-toggle=\'dropdown\' aria-haspopup=\'true\' aria-expanded=\'false\'>");
document.writeln("          4.0需求");
document.writeln("        </button>");
document.writeln("        <div class=\'dropdown-menu\'>");
document.writeln("          <a class=\'dropdown-item\' href=\'benefit\'>福利中心</a>");
document.writeln("          <a class=\'dropdown-item\' href=\'report_APP\'>APP戰報</a>");
document.writeln("          <a class=\'dropdown-item\' href=\'domain_list\'>域名列表</a>");
document.writeln("          <a class=\'dropdown-item\' href=\'fund_activity\'>充直紅包活動</a>");
document.writeln("        </div>");
document.writeln("    </div>");
document.writeln("    <div class=\'btn-group\'>");
document.writeln("        <button type=\'button\' class=\'btn btn-success dropdown-toggle dropdown-toggle-split\' data-toggle=\'dropdown\' aria-haspopup=\'true\' aria-expanded=\'false\'>");
document.writeln("          4.0功能查詢");
document.writeln("        </button>");
document.writeln("        <div class=\'dropdown-menu\'>");
document.writeln("          <a class=\'dropdown-item\' href=\'game_result\'>玩法/遊戲單號</a>");
document.writeln("          <a class=\'dropdown-item\' href=\'user_active\'>有效用戶/第三方銷量</a>");
document.writeln("          <a class=\'dropdown-item\' href=\'url_token\'>註冊碼/註冊連結/用戶資訊</a>");
document.writeln("          <a class=\'dropdown-item\' href=\'sun_user\'>太陽成/申博用戶</a>");
document.writeln("        </div>");
document.writeln("    </div>");
document.writeln("    <div class=\'btn-group\'>");
document.writeln("        <button type=\'button\' class=\'btn btn-info\'  onclick=location.href=\'/autoTest\'>");
document.writeln("          自動化測試");
document.writeln("        </button>");
document.writeln("    </div>");
/*document.writeln("    <div class=\'btn-group\'>");
//document.writeln("        <button type=\'button\' class=\'btn btn-warning\'  onclick=location.href=\'/stock_search\'>");
document.writeln("          股票");
document.writeln("        </button>");
document.writeln("    </div>");*/
document.writeln("    <div class=\'btn-group\'>");
document.writeln("        <button type=\'button\' class=\'btn btn-warning\'  onclick=location.href=\'/api_test\'>");
document.writeln("          API測試");
document.writeln("        </button>");
document.writeln("    </div>");
 
function pretty(js_path,split_){ //dataframe調整 文字版面 , js_path為element js定位, split_: 切各字元
    game_explan = document.querySelector(js_path)//
    explan_1 = game_explan.textContent.split(split_)[0]//用 #來分割
    explan_2 = game_explan.textContent.split(split_)[1]// #後
    game_explan.innerHTML = explan_1 + "<br>" +"<span>"+split_+explan_2+"</span>" //換行 ,增加span
}
function get_ip(){
    var ip = returnCitySN["cip"]+','+returnCitySN["cname"]
    console.log(ip)
    $.post(
        url = '/remote_IP',
        data = ip
    )
}
