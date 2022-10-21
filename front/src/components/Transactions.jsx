import React, { useState, useEffect } from "react";

const subtractMonths = (date, months) => {
      const result = new Date(date);
      result.setMonth(result.getMonth() - months);
      return result;
    };


function Transactions({ token }) {
    const [transactions, setTransactions] = useState([]);
    const [categories, setCategories] = useState([]);
    const [categoriesDict, setCategoriesDict] = useState({});
    const [transactionsNumber, setTransactionsNumber] = useState(0);
    const [categoriesNumber, setCategoriesNumber] = useState(0);

    const [startDate, setStartDate] = useState((subtractMonths(new Date(), 6)).toISOString().slice(0, 10));
    const [endDate, setEndDate] = useState(new Date().toISOString().slice(0, 10));
    const [searchCategory, setSearchCategory] = useState(null);
    const [selectedCategory, setSelectedCategory] = useState({});
    const [selectedTransaction, setSelectedTransaction] = useState({});

    const loadData = (start, end, category) =>{
        console.log(start)
        console.log(end)
        console.log(category)
        fetch('http://192.168.0.222:81/transactions?start_date='+start+'&end_date='+end+'&category='+category, {headers: {'Authorization': token}})
             .then((response) => response.json())
             .then((data) => {
                console.log(data);
                setTransactions(data.transactions);
                setTransactionsNumber(data.count)
             })
             .catch((err) => {
                console.log(err.message);
             });

        fetch('http://192.168.0.222:81/categories',{headers: {'Authorization': token}})
             .then((response) => response.json())
             .then((data) => {
                console.log(data);
                var dict = {};
                data.categories.map((category) => {
                    dict[category.id] = category.name
                });
                setCategories(data.categories);
                setCategoriesDict(dict);
                setCategoriesNumber(data.count)
             })
             .catch((err) => {
                console.log(err.message);
             });
    };

//     const updateTransactionType = (id, category) =>{
//         console.log(id,category)
//         //let transaction = transactions.find(o => o.id == id);
//         //setSelectedTransaction(transaction);
//         console.log(categories.find(o => o.id == category).income);
//         //setSelectedCategory(category);
//
//     };

const updateTransaction = async e => {
    e.preventDefault();
    console.log(e.target.elements.date.value,e.target.elements.sum.value,e.target.elements.category.value,e.target.elements.comment.value,e.target.elements.id.value)
    let date = e.target.elements.date.value;
    let sum = e.target.elements.sum.value;
    let category = e.target.elements.category.value;
    let comment = e.target.elements.comment.value;
    let id = e.target.elements.id.value;
    if (!(categories.find(o => o.id == category).income)) sum = sum * (-1);
    let result = await fetch('http://192.168.0.222:81/transactions?category='+category+'&date='+date+'&sum='+sum+'&comment='+comment+'&transaction='+id, { method: 'POST', headers: {'Authorization': token}})
    if (result.status == 201) loadData(startDate, endDate, searchCategory);

  }

const addTransaction = async e => {
    e.preventDefault();
    console.log(e.target.elements.date.value,e.target.elements.sum.value,e.target.elements.category.value,e.target.elements.comment.value)
    let date = e.target.elements.date.value;
    let sum = e.target.elements.sum.value;
    let category = e.target.elements.category.value;
    let comment = e.target.elements.comment.value;
    if (!(categories.find(o => o.id == category).income)) sum = sum * (-1);
    let result = await fetch('http://192.168.0.222:81/transactions?category='+category+'&date='+date+'&sum='+sum+'&comment='+comment, { method: 'PUT', headers: {'Authorization': token}})
    if (result.status == 201) {
        loadData(startDate, endDate, searchCategory);
        e.target.reset()
    }

  }

const deleteTransaction = async (id) => {

    console.log('Delete: '+id)

    let result = await fetch('http://192.168.0.222:81/transactions?transaction='+id, { method: 'DELETE', headers: {'Authorization': token}})
    if (result.status == 200) loadData(startDate, endDate, searchCategory);
  }

    useEffect(() => {
        loadData(startDate, endDate, searchCategory);
   }, [startDate, endDate, searchCategory]);

  return (
    <div className="container text-end mt-3 mb-3">


    <div className="row">
        <div className="col text-left">
            <h1>Транзакции</h1>

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
        <div className="row m-3">
            <div className="col text-right">Найдено транзакций: </div>
            <div className="col text-left col-2">{transactionsNumber}</div>
        </div>
        </div>
        <div className="col">
        <ul className="list-group m-2 justify-content-between mb-5">
            <li className={'list-group-item list-group-item-action text-dark bg-opacity-50 '}>
                <div data-bs-toggle="collapse" data-bs-target={"#collapseNew"} >
                                <div className="d-flex w-100 justify-content-center">
                                  <strong>Добавить</strong>
                                </div>

                </div>
                <div className="collapse" id={"collapseNew"}>
                                <div className="card card-body mt-2">
                                    <form onSubmit={addTransaction}>
                                      <div className="mb-3">
                                        <select name="category" className="form-select form-select-lg mb-3">
                                          {Object.entries(categoriesDict).map(([key, value]) => {
                                             return (
                                                    <option value={key} key={key} selected={key == searchCategory ? "selected" : false} >{value}</option>
                                             );
                                            })
                                          }
                                        </select>
                                      </div>
                                      <div className="form-floating mb-3">
                                        <input type="date" name="date" className="form-control" id="InputEnd" defaultValue={new Date().toISOString().slice(0, 10)}/>
                                        <label htmlFor="InputEnd">Дата</label>
                                      </div>
                                      <div className="input-group mb-3">
                                          <input type="text" name="sum" className="form-control" placeholder="Сумма" defaultValue="0" aria-describedby="basic-addon2" />
                                          <span className="input-group-text" id="basic-addon2">₽</span>
                                      </div>
                                      <div className="mb-3">
                                        <input type="text" name="comment" className="form-control" placeholder="Комментарий" id="exampleInputPassword1"/>
                                      </div>
                                      <div className="d-flex w-100 justify-content-center">
                                        <button type="submit" className="btn btn-success" >Добавить</button>
                                      </div>
                                    </form>
                                  </div>
                                </div>
            </li>
                {transactions.map((transaction) => {

                     return (

                            <li key={transaction.id} className={'list-group-item list-group-item-action text-dark bg-opacity-50 ' + (transaction.sum > 0 ? "bg-success" : "bg-danger")}  aria-current="true">
                                <div data-bs-toggle="collapse" data-bs-target={"#collapseExample"+transaction.id} >
                                <div className="d-flex w-100 justify-content-between">
                                  <small>{categoriesDict[transaction.category.toString()]}</small>
                                  <small>{new Date( Date.parse(transaction.date)).toLocaleString("ru", {year: 'numeric',month: 'long',day: 'numeric'})}</small>

                                </div>
                                <div className="d-flex w-100 justify-content-between">
                                    <small>{transaction.comment}</small><h5 className="mb-1"> {transaction.sum > 0 ? transaction.sum : transaction.sum * (-1)} ₽</h5>

                                </div>
                                </div>
                                <div className="collapse" id={"collapseExample"+transaction.id}>
                                  <div className="card card-body">
                                    <form onSubmit={updateTransaction}>
                                      <input type="text" className="visually-hidden" name="id" defaultValue={transaction.id} />
                                      <div className="mb-3">
                                        <select name="category" className="form-select form-select-lg mb-3" id={"category"+transaction.id}>
                                          {Object.entries(categoriesDict).map(([key, value]) => {
                                             return (
                                                    <option value={key} key={key} selected={key == transaction.category ? "selected" : false} >{value}</option>
                                             );
                                            })
                                          }
                                        </select>
                                      </div>
                                      <div className="form-floating mb-3">
                                        <input type="date" name="date" className="form-control" id="InputEnd" defaultValue={transaction.date}/>
                                        <label htmlFor="InputEnd">Дата</label>
                                      </div>
                                      <div className="input-group mb-3">
                                          <input type="text" name="sum" className="form-control" placeholder="Сумма" defaultValue={transaction.sum > 0 ? transaction.sum : transaction.sum * (-1)} aria-describedby="basic-addon2" />
                                          <span className="input-group-text" id="basic-addon2">₽</span>
                                      </div>
                                      <div className="mb-3">
                                        <input type="text" name="comment" className="form-control" placeholder="Комментарий" id="exampleInputPassword1" defaultValue={transaction.comment}/>
                                      </div>
                                      <div className="d-flex w-100 justify-content-between">
                                        <button type="button" className="btn btn-danger" onClick={e => deleteTransaction(transaction.id)}>Удалить</button>
                                        <button type="submit" className="btn btn-success" >Сохранить</button>
                                      </div>
                                    </form>
                                  </div>
                                </div>
                            </li>
                     );
                })}
        </ul>
        </div>
    </div>
    </div>
  );
}

export default Transactions;
