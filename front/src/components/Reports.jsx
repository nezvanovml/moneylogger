import React, { useState, useEffect } from "react";
import Alert from "./Alert.jsx";

const subtractMonths = (date, months) => {
      const result = new Date(date);
      result.setMonth(result.getMonth() - months);
      return result;
    };


function Reports({ token }) {
    const [transactions, setTransactions] = useState([]);
    const [categories, setCategories] = useState([]);
    const [categoriesDict, setCategoriesDict] = useState({});
    const [categoriesIncome, setCategoriesIncome] = useState({});
    const [transactionsNumber, setTransactionsNumber] = useState(0);
    const [categoriesNumber, setCategoriesNumber] = useState(0);

    const [startDate, setStartDate] = useState((subtractMonths(new Date(), 1)).toISOString().slice(0, 10));
    const [endDate, setEndDate] = useState(new Date().toISOString().slice(0, 10));
    const [searchCategory, setSearchCategory] = useState(null);

    const [income, setIncome] = useState(0);
    const [spent, setSpent] = useState(0);

    const [AlertMain, setAlertMain] = useState({'error':{'show': false, 'text': ''}, 'success': {'show': false, 'text': ''}});

    const count = () =>{
        let temp_spent = 0;
        let temp_income = 0;

        transactions.map((transaction) => {
                    if(categoriesIncome[transaction.category]) temp_income += transaction.sum;
                    else temp_spent += transaction.sum;
                });
        console.log(temp_income, temp_spent)
        setSpent(temp_spent)
        setIncome(temp_income)
    }

    const loadData =  (start, end, category) =>{


        fetch('/api/categories',{headers: {'Authorization': token}})
             .then((response) => response.json())
             .then((data) => {
                console.log(data);
                var dictName = {};
                var dictIncome = {};
                data.categories.map((category) => {
                    dictName[category.id] = category.name
                    dictIncome[category.id] = category.income
                });
                setCategories(data.categories);
                setCategoriesDict(dictName);
                setCategoriesIncome(dictIncome);
                setCategoriesNumber(data.count)

             })
             .catch((err) => {
                console.log(err.message);
             });

        fetch('/api/transactions?start_date='+start+'&end_date='+end+'&category='+category, {headers: {'Authorization': token}})
             .then((response) => response.json())
             .then((data) => {
                console.log(data);
                setTransactions(data.transactions).then(() => count());
                setTransactionsNumber(data.count)
             })
             .catch((err) => {
                console.log(err.message);
             });


    };


    useEffect( () => {
         loadData(startDate, endDate, searchCategory);

    }, [startDate, endDate, searchCategory]);

  return (
        <div className="container text-end mt-3 mb-3">
              <div className="row justify-content-md-center">
                    <div className="col-lg text-end">
                          <h1>Сводка</h1>
                          <form className=" ">
                                <select className="form-select form-select-lg mb-3" onChange={e => setSearchCategory(e.target.value)}>
                                      <option selected>Все категории</option>
                                      {Object.entries(categoriesDict).map(([key, value]) => {
                                         return (
                                                <option value={key} key={key}>{value}</option>
                                         );
                                      })}
                                </select>

                                <div className="form-floating mb-3">
                                        <input type="date" className="form-control" id="InputStart" defaultValue={startDate} onChange={e => setStartDate(e.target.value)}/>
                                        <label htmlFor="InputStart">Начало</label>
                                </div>
                                <div className="form-floating mb-3">
                                        <input type="date" className="form-control" id="InputEnd" defaultValue={endDate} onChange={e => setEndDate(e.target.value)}/>
                                        <label htmlFor="InputEnd">Конец</label>
                                </div>
                          </form>
                          <Alert source={AlertMain} />

                    </div>
                    <div className="col-lg ">
                          <div className="row justify-content-md-center">
                                <div className="col-lg-6 text-start fs-5">Число транзакций: {transactionsNumber}</div>
                                <div className="col-lg-6 text-start fs-5">Доход за период: {income.toLocaleString('ru', {style: 'currency', currency: 'RUB'})}</div>
                                <div className="col-lg-6 text-start fs-5">Расход за период: {spent.toLocaleString('ru', {style: 'currency', currency: 'RUB'})}</div>
                                <div className="col-lg-6 text-start fs-5">Баланс: {(income - spent).toLocaleString('ru', {style: 'currency', currency: 'RUB'})}</div>


                          </div>
                    </div>
              </div>
        </div>
  );
}

export default Reports;
