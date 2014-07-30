function dpmCtrl($scope, $location, page, invalidFlag, submitFlag) {
    
    $scope.invalidFlag = invalidFlag;

    if (page.firstPage === true) {
        $location.url(locList[page.count].url);
        page.firstPage = false;
    }
    $scope.nextPage = function nextPage(evnt, invalid) {
        if (invalid) {
            $scope.invalidFlag.policyName = true;
            $scope.invalidFlag.policyVersion = true;
            $scope.invalidFlag.policyAuthor = true;
            $scope.invalidFlag.policyCommunity = true;
        } else {
            $scope.invalidFlag.policyVersion = false;
            $scope.invalidFlag.policyAuthor = false;
            $scope.invalidFlag.policyCommunity = false;
            $scope.invalidFlag.policyName = false;
            if (page.count < maxPage) {
                page.count += 1;
                $location.url(locList[page.count].url);
            }
        }
    };
    $scope.prevPage = function prevPage() {
        flago = submitFlag.getObj();
        if (flago.submitted && !flago.flag) {
            flago.flag = true;
            flago.confirm = false;
            submitFlag.setObj(flago);
        }
        if (page.count > minPage) {
            page.count -= 1;
            $location.url(locList[page.count].url);
        }
    };
    $scope.firstPage = function () {
        var showP = true;
        if (page.count <= minPage) {
            showP = false;
        }
        return showP;
    };
    $scope.lastPage = function () {
        var showP = true;
        if (page.count >= maxPage) {
            showP = false;
        }
        return showP;
    };
    $scope.showSubmit = function() {
        var showS = false;
        var flago = submitFlag.getObj();
        if (flago.flag || page.count >= maxPage) {
            if (flago.submitted && !flago.flag) {
                showS = false;
            } else {
                showS = true;
            }
        }
        return showS;
    };
    $scope.showConfirm = function() {
        var showC = false;
        var flago = submitFlag.getObj();
        if (flago.confirm) {
            showC = true;
        }
        return showC;
    };
}
