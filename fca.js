
class Concept{
    constructor(intention, bit){
	this.subconcepts = [];
	this.extention = [];
	if (!bit) this.intention = new BinaryVector(intention);
	else this.intention = intention;
	this.root = true;
    }
    equivalent(c) {return this.intention.equals(c.intention);}
    intersection(c) {return new Concept(this.intention.intersection(c.intention), true);}
    createLabels(attr){
	this.attributes = [];	
	for(var i in attr) if (this.intention.get(i)) this.attributes.push(attr[i]);
    }
    subsumes(c) {return this.intersection(c).equivalent(this);}
    addSubConcept(c){
	var found = false;
	var toRemove = [];
	c.root = false;
	for(var sc in this.subconcepts){
	    var scc = this.subconcepts[sc];
	    if (scc.subsumes(c)) {found = true; break;}
	    if (c.subsumes(scc)) toRemove.push(sc);
	}
	if (!found) this.subconcepts.push(c);
	for (var tr in toRemove) this.subconcepts.splice(toRemove[tr], 1);
    }
}

class FormalContext{    
    constructor(attributes, objects, matrix){
	this.attributes = attributes;
	this.objects = objects;
	this.matrix = matrix;
	this.concepts = []		
    }
    // super basic algorithm to build
    // concepts (only intention)
    buildConcepts(){
	for(var i in this.matrix){
	    var c = new Concept(matrix[i], false);
	    this.addConcept(c);
	}
    }
    // basic function used for incremental
    // building of lattice
    addConcept(c){
	if (!this.conceptExist(c)) {
	   var toAdd = []
	    for (var oc in this.concepts){
		var nc = this.concepts[oc].intersection(c);
		if (!this.conceptExist(nc)) {
		    var found = false;
		    for (var cc in toAdd){
			if (toAdd[cc].equivalent(nc)) found = true;
		    }
		    if (!found) toAdd.push(nc);
		}
	    }
	    for (var oc in toAdd){
		this.concepts.push(toAdd[oc]);
	    }
	    if (!this.conceptExist(c)) {
		this.concepts.push(c);
	    }
	}
    }
    conceptExist(c){
	for (var i in this.concepts){
	    if (this.concepts[i].equivalent(c)) return true;
	}
	return false;
    }
    buildTaxonomy(){
	for(var c1 in this.concepts){
	    for(var c2 in this.concepts){
		if (c1!=c2){
		    var cc1 = this.concepts[c1];
		    var cc2 = this.concepts[c2];		    
		    if (cc1.subsumes(cc2) && !cc2.subsumes(cc1)) cc1.addSubConcept(cc2);
		    else if (cc2.subsumes(cc1)) cc2.addSubConcept(cc1);
		}
	    }
	}
    }
    addLabels(){
	for (var c in this.concepts){
	    this.concepts[c].createLabels(this.attributes);
	}
    }
    root(){
	var ret = [];
	for (var c in this.concepts){
	    if (this.concepts[c].root) ret.push(this.concepts[c]);	   
	}
	return ret;
    }
    // TODO: optimise by starting from root and going down only if needed
    populate(){
	for(var i in this.matrix){
	    var ci = new Concept(this.matrix[i], false);
	    for (var c in this.concepts){
		if (this.concepts[c].subsumes(ci)) this.concepts[c].extention.push(this.objects[i]);
	    }
	}
    }
}
