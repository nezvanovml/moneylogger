import React, { useState, useEffect } from "react";



function Categories({ token }) {
    const [categories, setCategories] = useState([]);
    const [categoriesNumber, setCategoriesNumber] = useState(0);

    const loadData = () =>{
        fetch('/api/categories',{headers: {'Authorization': token}})
             .then((response) => response.json())
             .then((data) => {
                console.log(data);
                setCategories(data.categories);
                setCategoriesNumber(data.count)
             })
             .catch((err) => {
                console.log(err.message);
             });
    };

    const updateCategory = async e => {
        e.preventDefault();
        let id = e.target.elements.id.value;
        let name = e.target.elements.name.value;
        let type = e.target.elements.type.value;
        let description = e.target.elements.description.value;
        if (type == 'income') type = 'True'
        else type = 'False'
        console.log(id, name, description, type)

        let result = await fetch('/api/categories?name='+name+'&description='+description+'&category='+id+'&income='+type, { method: 'POST', headers: {'Authorization': token}})
        if (result.status == 201) loadData();

    }

    const updateCategory = async e => {

        let id = e.target.elements.id.value;
        let name = e.target.elements.name.value;
        let income = e.target.elements.type.value;
        let description = e.target.elements.description.value;

        console.log(name, description)


        let result = await fetch('/api/categories?name='+name+'&description='+description+'&category='+id, { method: 'POST', headers: {'Authorization': token}})
        if (result.status == 201){
            loadData();
        }
        else {
            console.log(result)
        }

    }

    const addCategory = async e => {
        e.preventDefault();
        let name = e.target.elements.name.value;
        let type = e.target.elements.type.value;
        let description = e.target.elements.description.value;

        console.log(name, type, description)

        if (type == 'income') type = 'True'
        else type = 'False'

        let result = await fetch('/api/categories?name='+name+'&income='+type+'&description='+description, { method: 'PUT', headers: {'Authorization': token}})
        if (result.status == 201) {
            loadData();
            e.target.reset()
        }
    }

    const deleteCategory = async (id) => {
        console.log('Delete: '+id)
        let result = await fetch('/api/categories?category='+id, { method: 'DELETE', headers: {'Authorization': token}})
        if (result.status == 200) loadData();
    }

    useEffect(() => {
        loadData();
    }, []);

  return (
        <div className="container text-end mt-3 mb-3">
              <div className="row">
                    <div className="col text-left">
                          <h1>Категории</h1>

                          <div className="row m-3">
                                <div className="col text-right fs-5">Найдено категорий: </div>
                                <div className="col text-left col-2 fs-5">{categoriesNumber}</div>
                          </div>
                    </div>
                    <div className="col">
                          <ul className="list-group m-2 justify-content-between mb-5">
                                <li className={'list-group-item list-group-item-action text-dark bg-opacity-50 '}>
                                        <div data-bs-toggle="collapse" data-bs-target={"#collapseNew"} >
                                                <div className="d-flex w-100 justify-content-center fs-5">
                                                        <strong>Добавить категорию</strong>
                                                </div>

                                        </div>
                                        <div className="collapse" id={"collapseNew"}>
                                                <div className="card card-body mt-2">
                                                        <form onSubmit={addCategory}>
                                                                <div className="mb-3">
                                                                        <input type="text" name="name" className="form-control" placeholder="Название" defaultValue="" aria-describedby="basic-addon2" />
                                                                </div>
                                                                <div className="mb-3">
                                                                        <input type="text" name="description" className="form-control" placeholder="Описание"/>
                                                                </div>
                                                                <div className="d-flex w-100 justify-content-around mb-3">
                                                                        <input type="radio" className="btn-check" value="income" name="type" id="success-outlined" autoComplete="off"  />
                                                                        <label className="btn btn-outline-success" htmlFor="success-outlined">Доход</label>
                                                                        <input type="radio" className="btn-check" value="spent" name="type" id="danger-outlined" autoComplete="off" defaultChecked={true} />
                                                                        <label className="btn btn-outline-danger" htmlFor="danger-outlined">Расход</label>
                                                                </div>
                                                                <div className="d-flex w-100 justify-content-center">
                                                                    <button type="submit" className="btn btn-primary" >Добавить</button>
                                                                </div>
                                                        </form>
                                                </div>
                                        </div>
                                </li>
                                {categories.map((category) => {
                                    return (
                                <li key={category.id} className={'list-group-item list-group-item-action text-dark bg-opacity-50 ' + (category.income ? "bg-success" : "bg-danger")}  aria-current="true">
                                        <div data-bs-toggle="collapse" data-bs-target={"#collapseExample"+category.id} >
                                                <div className="d-flex w-100 justify-content-between fs-6">
                                                        {category.name}
                                                </div>
                                        </div>
                                        <div className="collapse" id={"collapseExample"+category.id}>
                                                <div className="card card-body">
                                                        <form onSubmit={updateCategory}>
                                                                <input type="text" className="visually-hidden" name="id" defaultValue={category.id} />
                                                                <div className="mb-3">
                                                                        <input type="text" name="name" className="form-control" placeholder="Название" defaultValue={category.name} aria-describedby="basic-addon2" />
                                                                </div>
                                                                <div className="mb-3">
                                                                        <input type="text" name="description" className="form-control" placeholder="Описание" defaultValue={category.description}/>
                                                                </div>
                                                                <div className="d-flex w-100 justify-content-around mb-3">
                                                                        <input type="radio" className="btn-check" value="income" name="type" id="success-outlined" checked ={category.income} />
                                                                        <label className="btn btn-outline-success" htmlFor="success-outlined">Доход</label>
                                                                        <input type="radio" className="btn-check" value="spent" name="type" id="danger-outlined" checked ={!category.income} />
                                                                        <label className="btn btn-outline-danger" htmlFor="danger-outlined">Расход</label>
                                                                </div>
                                                                <div className="d-flex w-100 justify-content-between">
                                                                        <button type="button" className="btn btn-danger" onClick={e => deleteCategory(category.id)}>Удалить</button>
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

export default Categories;
