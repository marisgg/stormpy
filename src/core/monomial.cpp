/*
 * monomial.cpp
 *
 *  Created on: 16 Apr 2016
 *      Author: harold
 */

#include "monomial.h"


#include "src/types.h"
#include "src/helpers.h"

void define_monomial(py::module& m) {
    py::class_<Monomial, std::shared_ptr<Monomial>>(m, "Monomial")

        .def("__pow__", [](const Monomial::Arg& var, carl::uint exp) {return var->pow(exp);})
        .def("__mul__",  static_cast<Monomial::Arg (*)(const Monomial::Arg&, const Monomial::Arg&)>(&carl::operator*))
        .def("__mul__",  static_cast<Monomial::Arg (*)(const Monomial::Arg&, carl::Variable::Arg)>(&carl::operator*))
        .def("__mul__",  static_cast<Monomial::Arg (*)(carl::Variable::Arg, const Monomial::Arg&)>(&carl::operator*))

        .def("__pos__", [](const Monomial::Arg& var) {return Monomial::Arg(var);})

        .def_property_readonly("tdeg", [](const Monomial::Arg& arg) { return arg->tdeg();} )
        .def_property_readonly("exponents", [](const Monomial::Arg& arg) { return arg->exponents();} )
        .def("__str__", &streamToString<const Monomial::Arg&>)

        .def("__len__", [](const Monomial::Arg& m) { return m->nrVariables(); })
        .def("__getitem__", [](const Monomial::Arg& m, std::size_t index) { return *(m->begin()+index); })
        .def("__iter__", [](const Monomial::Arg& m) { return py::make_iterator(m->begin(), m->end()); },
                            py::keep_alive<0, 1>() /* Essential: keep object alive while iterator exists */)
        .def("__getstate__", [](const Monomial& val) -> std::tuple<std::string> { throw NoPickling(); })
        .def("__setstate__", [](Monomial& val, const std::tuple<std::string>& data) { throw NoPickling(); })
        .def("__hash__", [](const Monomial& v) { std::hash<Monomial> h; return h(v);});


    m.def("create_monomial", [] (const carl::Variable& v, carl::exponent e){
        return carl::createMonomial(v, e);
    }, "Create monomial", py::arg("variable"), py::arg("exponent"));
    m.def("clear_monomial_pool", [](){
        carl::MonomialPool::getInstance().clear();
    }, "Clear monomial pool and remove all monomials");

}
