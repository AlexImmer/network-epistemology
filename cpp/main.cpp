#include <iostream>
#include <unordered_map>
#include <vector>
#include <fstream>
#include <sstream>
#include <queue>

#include <boost/serialization/vector.hpp>
#include <boost/serialization/string.hpp>
#include <boost/serialization/unordered_map.hpp>
#include <boost/archive/binary_iarchive.hpp>
#include <boost/archive/binary_oarchive.hpp>

#include "io.h"

//#define SRLZ 1

using namespace std;

int main(int argc, char *argv[]) {
#ifdef SRLZ
    string path = argv[1];

    cerr << "Reading author file" << endl;
    read_authors(path);

    cerr << "Reading publication file" << endl;
    read_publications(path);

    cerr << "Reading coauthorship info" << endl;
    read_edges(path, "coauthorship.csv", COAUTHORSHIP_EDGE);

    cerr << "Reading citation data" << endl;
    read_edges(path, "citation.csv", CITATION_EDGE);

    cerr << "Reading authorship data" << endl;
    read_edges(path, "pub_auth.csv", AUTHORSHIP_EDGE);

    ofstream ofs("/Users/milenkoviclazar/sandbox/network-epistemology/cpp/serialized/serialized.bak");
    boost::archive::binary_oarchive oa(ofs);
    oa << author_ids << publication_ids << names << pub_infos << adj << V;
    ofs.close();
#endif
    ifstream ifs("/Users/milenkoviclazar/sandbox/network-epistemology/cpp/serialized/serialized.bak");
    boost::archive::binary_iarchive ia(ifs);
    ia >> author_ids >> publication_ids >> names >> pub_infos >> adj >> V;
    
    return 0;
}