`timescale 1ps/1ps
module rdma_parser_packer_tb;
reg clk;
    reg rst;
    
    initial clk = 0;
    initial rst = 1;
    always #2500 clk =~clk;
    
    initial #10000 rst = 0;
    
    //Input AXI Stream Interface
reg  [63   : 0]    data_slave;
reg  [7    : 0]    keep_slave;
reg  [0    : 0]    valid_slave;
reg  [0    : 0]    last_slave;
wire [0    : 0]    ready_slave;

//Output AXI Stream Interface
wire [63   : 0]    data_master;
wire [7    : 0]    keep_master;
wire [0    : 0]    valid_master;
wire [0    : 0]    last_master;
wire [0    : 0]    ready_master;
wire [63   : 0]    data_master1;
wire [7    : 0]    keep_master1;
wire [0    : 0]    valid_master1;
wire [0    : 0]    last_master1;
wire [0    : 0]    ready_master1;
wire [63   : 0]    data_master2;
wire [7    : 0]    keep_master2;
wire [0    : 0]    valid_master2;
wire [0    : 0]    last_master2;
wire [0    : 0]    ready_master2;
wire [63   : 0]    data_master3;
wire [7    : 0]    keep_master3;
wire [0    : 0]    valid_master3;
wire [0    : 0]    last_master3;
reg  [0    : 0]    ready_master3;

//Input results
reg  [15   : 0]    src_port;
wire [15   : 0]    src_port1;
wire [15   : 0]    src_port3;
reg  [15   : 0]    dst_address;
wire [15   : 0]    dst_address1;
wire [15   : 0]    dst_address3;
reg  [15   : 0]    length;
wire [15   : 0]    length1;
wire [15   : 0]    length3;
reg  [15   : 0]    checksum;
wire [15   : 0]    checksum1;
wire [15   : 0]    checksum3;
integer i;
integer seed;


    initial
    begin
    src_port = 0;
dst_address = 0;
length = 0;
checksum = 0;
seed = 0;

wait(!rst);

    interval;
    burst('hc53e,'hd755,'h10,'h8490,'h82e2e662f728b4fa,'d2);
    interval;
    
    wait(valid_master3);
if(src_port3 != 'hc53e)
$display("src_port unmatch@length 2");
else
$display("src_port match@length 2");

if(dst_address3 != 'hd755)
$display("dst_address unmatch@length 2");
else
$display("dst_address match@length 2");

if(length3 != 'h10)
$display("length unmatch@length 2");
else
$display("length match@length 2");

if(checksum3 != 'h8490)
$display("checksum unmatch@length 2");
else
$display("checksum match@length 2");

burst('hcf53,'h9b4b,'h18,'hb752,'h8133287637ebdcd9,'d3);
    interval;
    
    wait(valid_master3);
if(src_port3 != 'hcf53)
$display("src_port unmatch@length 3");
else
$display("src_port match@length 3");

if(dst_address3 != 'h9b4b)
$display("dst_address unmatch@length 3");
else
$display("dst_address match@length 3");

if(length3 != 'h18)
$display("length unmatch@length 3");
else
$display("length match@length 3");

if(checksum3 != 'hb752)
$display("checksum unmatch@length 3");
else
$display("checksum match@length 3");

burst('h904d,'h478c,'h20,'h8042,'he6f4590b9a164106,'d4);
    interval;
    
    wait(valid_master3);
if(src_port3 != 'h904d)
$display("src_port unmatch@length 4");
else
$display("src_port match@length 4");

if(dst_address3 != 'h478c)
$display("dst_address unmatch@length 4");
else
$display("dst_address match@length 4");

if(length3 != 'h20)
$display("length unmatch@length 4");
else
$display("length match@length 4");

if(checksum3 != 'h8042)
$display("checksum unmatch@length 4");
else
$display("checksum match@length 4");

burst('h9ecb,'h3291,'h28,'ha90f,'h8f4ff31e78de5857,'d5);
    interval;
    
    wait(valid_master3);
if(src_port3 != 'h9ecb)
$display("src_port unmatch@length 5");
else
$display("src_port match@length 5");

if(dst_address3 != 'h3291)
$display("dst_address unmatch@length 5");
else
$display("dst_address match@length 5");

if(length3 != 'h28)
$display("length unmatch@length 5");
else
$display("length match@length 5");

if(checksum3 != 'ha90f)
$display("checksum unmatch@length 5");
else
$display("checksum match@length 5");

burst('hb524,'hde4b,'h30,'h68b1,'h8d723104f77383c1,'d6);
    interval;
    
    wait(valid_master3);
if(src_port3 != 'hb524)
$display("src_port unmatch@length 6");
else
$display("src_port match@length 6");

if(dst_address3 != 'hde4b)
$display("dst_address unmatch@length 6");
else
$display("dst_address match@length 6");

if(length3 != 'h30)
$display("length unmatch@length 6");
else
$display("length match@length 6");

if(checksum3 != 'h68b1)
$display("checksum unmatch@length 6");
else
$display("checksum match@length 6");

burst('he2a8,'h855f,'h38,'h730,'h9ca5499d004ae545,'d7);
    interval;
    
    wait(valid_master3);
if(src_port3 != 'he2a8)
$display("src_port unmatch@length 7");
else
$display("src_port match@length 7");

if(dst_address3 != 'h855f)
$display("dst_address unmatch@length 7");
else
$display("dst_address match@length 7");

if(length3 != 'h38)
$display("length unmatch@length 7");
else
$display("length match@length 7");

if(checksum3 != 'h730)
$display("checksum unmatch@length 7");
else
$display("checksum match@length 7");

end

always@(posedge clk or posedge rst) begin
        if (rst)
            ready_master3 = 0;
        else
            ready_master3 = $random(seed)%2;
    end
    
    rdma_packer rdma_packer0(
.clk(clk),
.rst(rst),
//Input AXI Stream Interface
.data_slave(data_slave),
.keep_slave(keep_slave),
.valid_slave(valid_slave),
.last_slave(last_slave),
.ready_slave(ready_slave),

//Input results
.src_port(src_port),
.dst_address(dst_address),
.length(length),
.checksum(checksum),

//Output AXI Stream Interface
.data_master  (data_master ),
.keep_master  (keep_master ),
.valid_master (valid_master),
.last_master  (last_master ),
.ready_master (ready_master)
);

rdma_packer rdma_packer1(
.clk(clk),
.rst(rst),
//Input AXI Stream Interface
.data_slave(data_master1),
.keep_slave(keep_master1),
.valid_slave(valid_master1),
.last_slave(last_master1),
.ready_slave(ready_master1),

//Input results
.src_port(src_port1),
.dst_address(dst_address1),
.length(length1),
.checksum(checksum1),

//Output AXI Stream Interface
.data_master  (data_master2),
.keep_master  (keep_master2),
.valid_master (valid_master2),
.last_master  (last_master2),
.ready_master (ready_master2)
);

rdma_parser rdma_parser0(
.clk(clk),
.rst(rst),
//Input AXI Stream Interface
.data_slave(data_master),
.keep_slave(keep_master),
.valid_slave(valid_master),
.last_slave(last_master),
.ready_slave(ready_master),

//Input results
.src_port(src_port1),
.dst_address(dst_address1),
.length(length1),
.checksum(checksum1),

//Output AXI Stream Interface
.data_master  (data_master1),
.keep_master  (keep_master1),
.valid_master (valid_master1),
.last_master  (last_master1),
.ready_master (ready_master1)
);

rdma_parser rdma_parser1(
.clk(clk),
.rst(rst),
//Input AXI Stream Interface
.data_slave(data_master2),
.keep_slave(keep_master2),
.valid_slave(valid_master2),
.last_slave(last_master2),
.ready_slave(ready_master2),

//Input results
.src_port(src_port3),
.dst_address(dst_address3),
.length(length3),
.checksum(checksum3),

//Output AXI Stream Interface
.data_master  (data_master3),
.keep_master  (keep_master3),
.valid_master (valid_master3),
.last_master  (last_master3),
.ready_master (ready_master3)
);

task burst(
    input  [15   : 0]    src_port_tsk,
input  [15   : 0]    dst_address_tsk,
input  [15   : 0]    length_tsk,
input  [15   : 0]    checksum_tsk,
input  [63   : 0]    data_tsk,
    input  [31   : 0]    length_tsk
    );
    reg flag;
    begin
        i = 0;
        flag = 0;
        @(posedge clk);
        while(i < length_tsk - 1)
        begin
            data_slave  = data_tsk;
            valid_slave = 1;
            keep_slave  = -1;
            last_slave  = 0;
            src_port = src_port_tsk;
        dst_address = dst_address_tsk;
        length = length_tsk;
        checksum = checksum_tsk;

    
            @(posedge clk);
            //if (ready_slave) $display ("1");
            if (ready_slave) i = i + 1;
            else             i = i;
            
        end
    
        do begin
            data_slave  = data_tsk;
            valid_slave = 1;
            keep_slave  = -1;
            last_slave  = 1;
            src_port = src_port_tsk;
        dst_address = dst_address_tsk;
        length = length_tsk;
        checksum = checksum_tsk;

            #1;
            if (ready_slave) flag = 1;
            @(posedge clk);
        end while(~flag);
            
    end
    endtask
    
    task interval;
    begin
            data_slave  = 0;
            valid_slave = 0;
            keep_slave  = 0;
            last_slave  = 0;
        
    end
    endtask
    
    endmodule